declare const bootstrap: any;
/*
    * Allow the user to delete track(s) from a playlist
    * When the user clicks the "Edit" button:
        * The Delete and Cancel buttons shall both appear
        * The user can tick the checkbox on each row to indicate that the playlist will be deleted
        * When they click the Delete button:
            * A pop-up will ask for their confirmation
            * If they hit cancel they pop-up disappears
            * If they delete, the page will refresh and the deleted track(s) will no longer be shown in the playlist
        * When they click the Cancel button:
            * The Delete, Cancel and checkboxes will disappear
*/

export function init(): void {
    //Declare const HTML variables
    const editBtn = document.querySelector<HTMLButtonElement>('#edit-playlist-tracks-btn');
    const deleteBtn = document.querySelector<HTMLButtonElement>('#delete-playlist-tracks-btn');
    const cancelBtn = document.querySelector<HTMLButtonElement>('#cancel-edit-btn');
    const checkboxCells = document.querySelectorAll<HTMLElement>('.playlist-track-checkbox-cell');
    const checkboxHeader = document.querySelector<HTMLElement>('.checkbox-header');
    const confirmDeleteBtn = document.querySelector<HTMLButtonElement>('#confirm-delete-btn');
    const modalElement = document.getElementById('confirmDeleteModal');

    //Check that all const exist
    if (!editBtn || !deleteBtn || !cancelBtn || !checkboxCells || !checkboxHeader || !confirmDeleteBtn || !modalElement) {
        console.warn("Required elements not found:", {
            editBtn: !!editBtn,
            deleteBtn: !!deleteBtn,
            cancelBtn: !!cancelBtn,
            checkboxCells: !!checkboxCells,
            checkboxHeader: !!checkboxHeader,
            confirmDeleteBtn: !!confirmDeleteBtn,
            modalElement: !!modalElement
        });
        return;
    }

    //Define additional variables
    const selectedPlaylistTrackIds = new Set<number>();
    const modal = modalElement ? new bootstrap.Modal(modalElement) : null;
    const csrfToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1] ?? '';

    //Edit button actions
    editBtn.addEventListener('click', (): void => {
        checkboxHeader.classList.remove('d-none');
        checkboxCells.forEach((field: HTMLElement): void => {
            field.classList.remove('d-none');
        });
        deleteBtn.classList.remove('d-none');
        cancelBtn.classList.remove('d-none');
        editBtn.classList.add('d-none');
    });

    //Cancel button actions
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

    //Delete button actions
    deleteBtn.addEventListener('click', (): void => {
        selectedPlaylistTrackIds.clear();
        checkboxCells.forEach((cell: HTMLElement): void => {
            const checkbox = cell.querySelector<HTMLInputElement>('input[type="checkbox"]');
            const row = cell.closest<HTMLElement>('tr');
            const playlistTrackId = row?.dataset.playlistTrackId;
            if (checkbox && checkbox.checked && playlistTrackId) {
                selectedPlaylistTrackIds.add(parseInt(playlistTrackId));
            }
        });
        modal?.show();
    });

    //Confirm delete button actions
    confirmDeleteBtn.addEventListener('click', (): void => {
        const payload = JSON.stringify({ playlist_track_id: [...selectedPlaylistTrackIds] });
        const deleteUrl = confirmDeleteBtn.dataset.deleteUrl ?? '';

        fetch(deleteUrl, {
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
            console.error('Error deleting playlist tracks:', error);
        });
    });

    console.log('deletePlaylistTracks initialized');
}

document.addEventListener('DOMContentLoaded', init);