# notes/views.py
import os, uuid, time
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from django.utils.text import slugify
from django.contrib.auth.hashers import check_password # NEW IMPORT

from .forms import NoteForm, SearchForm, NoteUnlockForm # NEW IMPORT
from .models import NoteManager
from .templatetags.note_extras import markdown_and_links

# (nm, _add_safe_id, and _handle_file_uploads helpers are unchanged)
_note_manager: NoteManager | None = None
def nm() -> NoteManager:
    global _note_manager
    if _note_manager is None: _note_manager = NoteManager()
    return _note_manager
def _add_safe_id(note):
    if note: note["id"] = str(note["_id"])
    return note
def _handle_file_uploads(files):
    saved_paths = []
    if not os.path.exists(settings.MEDIA_ROOT): os.makedirs(settings.MEDIA_ROOT)
    for f in files:
        original_name, ext = os.path.splitext(f.name)
        sanitized_name = slugify(original_name)
        timestamp = int(time.time())
        filename = f"{timestamp}-{sanitized_name}{ext}"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        with open(filepath, 'wb+') as destination:
            for chunk in f.chunks(): destination.write(chunk)
        saved_paths.append(filename)
    return saved_paths

# --- HTML Views ---
# (note_list is unchanged)
def note_list(request):
    manager = nm()

    # Handle the POST request for bulk deletion
    if request.method == "POST":
        note_ids_to_delete = request.POST.getlist('selected_notes')
        
        # --- NEW: Server-side check for password protection ---
        unprotected_note_ids = []
        for note_id in note_ids_to_delete:
            note = manager.get(note_id)
            if note and not note.get("password"):
                unprotected_note_ids.append(note_id)
        
        if unprotected_note_ids:
            manager.delete_many(unprotected_note_ids)
            
        return redirect('note_list')

    # The original GET request logic remains the same
    form = SearchForm(request.GET)
    query = request.GET.get('q', '')
    notes = manager.search(query) if query else manager.all()
    
    for note in notes:
        _add_safe_id(note)
        
    return render(request, "notes/note_list.html", {"notes": notes, "form": form})
# --- MODIFIED ---
def note_detail(request, pk):
    manager = nm()
    note = manager.get(pk) or _404()
    _add_safe_id(note)

    # Password protection logic
    is_locked = note.get("password")
    unlocked_notes_session = request.session.get('unlocked_notes', [])

    if is_locked and note['id'] not in unlocked_notes_session:
        if request.method == "POST":
            form = NoteUnlockForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                if check_password(password, note['password']):
                    unlocked_notes_session.append(note['id'])
                    request.session['unlocked_notes'] = unlocked_notes_session
                    # Fall through to render the note
                else:
                    form.add_error('password', 'Incorrect password.')
        else: # GET request
            form = NoteUnlockForm()
        
        # If still not unlocked, render the unlock form and stop
        if note['id'] not in request.session.get('unlocked_notes', []):
            return render(request, "notes/note_unlock_form.html", {"note": note, "form": form})

    # Original logic for unlocked notes
    note['rendered_content'] = markdown_and_links(note.get('content', ''))
    context = {"note": note, "MEDIA_URL": settings.MEDIA_URL}
    return render(request, "notes/note_detail.html", context)

# --- MODIFIED ---
def note_create(request):
    manager = nm()
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            attachment_paths = _handle_file_uploads(request.FILES.getlist('attachments'))
            manager.create(
                title=data['title'],
                content=data['content'],
                tags=data['tags'],
                is_pinned=data['is_pinned'],
                attachments=attachment_paths,
                password=data.get('password') # Pass password
            )
            return redirect("note_list")
    else:
        form = NoteForm()
    return render(request, "notes/note_form.html", {"form": form, "is_new": True})

# --- MODIFIED ---
def note_edit(request, pk):
    manager = nm()
    note = manager.get(pk) or _404()
    _add_safe_id(note)
    if isinstance(note.get('tags'), list): note['tags'] = ', '.join(note['tags'])

    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            new_paths = _handle_file_uploads(request.FILES.getlist('attachments'))
            existing_paths = note.get('attachments', [])
            all_paths = existing_paths + new_paths
            manager.update(
                pk,
                title=data['title'],
                content=data['content'],
                tags=data['tags'],
                is_pinned=data['is_pinned'],
                attachments=all_paths,
                password=data.get('password') # Pass password
            )
            return redirect("note_detail", pk=pk)
    else:
        form = NoteForm(initial=note)
    return render(request, "notes/note_form.html", {"form": form, "is_new": False, "note": note})

# (note_delete, _404, and api_notes are unchanged)
def note_delete(request, pk):
    manager = nm()
    note = manager.get(pk) or _404()
    _add_safe_id(note)
    
    # Initialize the form for both GET and POST requests
    form = NoteUnlockForm(request.POST or None)

    if request.method == "POST":
        # Case 1: The note is password-protected
        if note.get("password"):
            if form.is_valid():
                password = form.cleaned_data['password']
                if check_password(password, note['password']):
                    # Password is correct, proceed with deletion
                    manager.delete(pk)
                    return redirect("note_list")
                else:
                    # Password is incorrect, add an error to the form
                    form.add_error('password', 'Incorrect password. Deletion failed.')
            # If form is invalid, it will be re-rendered with errors below
        
        # Case 2: The note is not protected
        else:
            manager.delete(pk)
            return redirect("note_list")

    # For GET requests, or if a POST request fails validation
    context = {
        "note": note,
        "form": form if note.get("password") else None
    }
    return render(request, "notes/note_confirm_delete.html", context)
def _404():
    raise Http404("Note not found")
@require_GET
def api_notes(request):
    notes = nm().all()
    for note in notes: _add_safe_id(note)
    return JsonResponse({"notes": notes}, safe=False)
