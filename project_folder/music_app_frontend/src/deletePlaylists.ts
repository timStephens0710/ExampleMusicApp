import * as bootstrap from 'bootstrap';
/*
    * Allow the user to delete playlist(s)
    * When the user clicks the "Edit" button:
        * The Delete and Cancel buttons shall both appear
        * The user can tick the checkbox on each row to indicate that the playlist will be deleted
        * When they click the Delete button:
            * A pop-up will ask for their confirmation
            * If they hit cancel they pop-up disappears
            * If they delete, the page will refresh and the deleted playlist(s) will no longer be shown
        * When they click the Cancel button:
            * The Delete, Cancel and checkboxes will disappear
*/

export function init(): void {
    const editBtn = document.querySelector<HTMLButtonElement>('#edit-playlists-btn');
    const deleteBtn = document.querySelector<HTMLButtonElement>('#delete-playlists-btn');
    const cancelBtn = document.querySelector<HTMLButtonElement>('#cancel-edit-btn');
    const checkboxCells = document.querySelectorAll<HTMLElement>('.playlist-checkbox-cell');
    const checkboxHeader = document.querySelector<HTMLElement>('.checkbox-header');
    const confirmDeleteBtn = document.querySelector<HTMLButtonElement>('#confirm-delete-btn');

    if (!editBtn || !deleteBtn || !cancelBtn || !confirmDeleteBtn || !checkboxHeader) {
        console.warn('Delete playlist: required elements not found');
        return;
    }

    const selectedPlaylistIds = new Set<number>();

    const modalElement = document.getElementById('confirmDeleteModal');
    const modal = modalElement ? new bootstrap.Modal(modalElement) : null;

    const csrfToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1] ?? '';

    editBtn.addEventListener('click', (): void => {
        checkboxHeader.classList.remove('d-none');
        checkboxCells.forEach((field: HTMLElement): void => {
            field.classList.remove('d-none');
        });
        deleteBtn.classList.remove('d-none');
        cancelBtn.classList.remove('d-none');
        editBtn.classList.add('d-none');
    });

    cancelBtn.addEventListener('click', (): void => {
        checkboxHeader.classList.add('d-none');
        checkboxCells.forEach((cell: HTMLElement): void => {
            cell.classList.add('d-none');
            const checkbox = cell.querySelector<HTMLInputElement>('input[type="checkbox"]');
            if (checkbox) checkbox.checked = false;
        });
        deleteBtn.classList.add('d-none');
        cancelBtn.classList.add('d-none');
        editBtn.classList.remove('d-none');
    });

    deleteBtn.addEventListener('click', (): void => {
        selectedPlaylistIds.clear();
        checkboxCells.forEach((cell: HTMLElement): void => {
            const checkbox = cell.querySelector<HTMLInputElement>('input[type="checkbox"]');
            const row = cell.closest<HTMLElement>('tr');
            const playlistId = row?.dataset.playlistId;
            if (checkbox && checkbox.checked && playlistId) {
                selectedPlaylistIds.add(parseInt(playlistId));
            }
        });
        modal?.show();
    });

    confirmDeleteBtn.addEventListener('click', (): void => {
        const urlPathSegments = window.location.pathname.split('/');
        const username = urlPathSegments[1];
        const payload = JSON.stringify({ playlist_id: [...selectedPlaylistIds] });

        fetch(`/${username}/your_playlists/delete_playlists`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: payload
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                modal?.hide();
                checkboxCells.forEach((cell: HTMLElement): void => {
                    const checkbox = cell.querySelector<HTMLInputElement>('input[type="checkbox"]');
                    if (checkbox) checkbox.checked = false;
                });
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Error deleting playlists:', error);
        });
    });

    console.log('deletePlaylists initialized');
}

document.addEventListener('DOMContentLoaded', init);