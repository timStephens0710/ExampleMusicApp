import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { init } from '../src/deletePlaylists';

// ─── Mock bootstrap ──────────────────────────────────────────────────────────

const mockShow = vi.fn();
const mockHide = vi.fn();

vi.mock('bootstrap', () => ({
    Modal: vi.fn().mockImplementation(function(this: any) {
        this.show = mockShow;
        this.hide = mockHide;
    }),
}));

// ─── Mock fetch ───────────────────────────────────────────────────────────────

const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// ─── DOM Setup ───────────────────────────────────────────────────────────────

function buildDOM(): void {
    document.body.innerHTML = `
        <table>
            <thead>
                <tr><th class="checkbox-header d-none"></th><th>Name</th></tr>
            </thead>
            <tbody>
                <tr class="row_table" data-playlist-id="1">
                    <td class="playlist-checkbox-cell d-none">
                        <input type="checkbox" class="playlist-checkbox">
                    </td>
                    <td>Test Playlist</td>
                </tr>
                <tr class="row_table" data-playlist-id="2">
                    <td class="playlist-checkbox-cell d-none">
                        <input type="checkbox" class="playlist-checkbox">
                    </td>
                    <td>WIP Playlist</td>
                </tr>
            </tbody>
        </table>
        <button id="edit-playlists-btn">Edit Playlists</button>
        <button id="delete-playlists-btn" class="d-none">Delete</button>
        <button id="cancel-edit-btn" class="d-none">Cancel</button>
        <div id="confirmDeleteModal">
            <button id="confirm-delete-btn">Delete</button>
        </div>`;
}

// ─── Tests ───────────────────────────────────────────────────────────────────

describe('delete_playlists.ts', () => {

    beforeEach(() => {
        vi.clearAllMocks();
        vi.stubGlobal('fetch', mockFetch);
        Object.defineProperty(document, 'cookie', {
            writable: true,
            value: 'csrftoken=testcsrftoken123',
        });
        buildDOM();
        init();
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    // ── 1. Edit button ────────────────────────────────────────────────────────

    describe('Edit button', () => {
        it('shows checkboxes, delete and cancel buttons — and hides itself', () => {
            const editBtn = document.getElementById('edit-playlists-btn')!;
            const deleteBtn = document.getElementById('delete-playlists-btn')!;
            const cancelBtn = document.getElementById('cancel-edit-btn')!;
            const checkboxHeader = document.querySelector('.checkbox-header')!;
            const checkboxCells = document.querySelectorAll('.playlist-checkbox-cell');

            editBtn.click();

            expect(editBtn.classList.contains('d-none')).toBe(true);
            expect(deleteBtn.classList.contains('d-none')).toBe(false);
            expect(cancelBtn.classList.contains('d-none')).toBe(false);
            expect(checkboxHeader.classList.contains('d-none')).toBe(false);
            checkboxCells.forEach(cell => {
                expect(cell.classList.contains('d-none')).toBe(false);
            });
        });
    });

    // ── 2. Cancel button ──────────────────────────────────────────────────────

    describe('Cancel button', () => {
        it('resets to default view and unchecks all checkboxes', () => {
            const editBtn = document.getElementById('edit-playlists-btn')!;
            const deleteBtn = document.getElementById('delete-playlists-btn')!;
            const cancelBtn = document.getElementById('cancel-edit-btn')!;
            const checkboxHeader = document.querySelector('.checkbox-header')!;
            const checkboxCells = document.querySelectorAll<HTMLElement>('.playlist-checkbox-cell');

            editBtn.click();
            checkboxCells.forEach(cell => {
                const cb = cell.querySelector<HTMLInputElement>('input[type="checkbox"]');
                if (cb) cb.checked = true;
            });
            cancelBtn.click();

            expect(editBtn.classList.contains('d-none')).toBe(false);
            expect(deleteBtn.classList.contains('d-none')).toBe(true);
            expect(cancelBtn.classList.contains('d-none')).toBe(true);
            expect(checkboxHeader.classList.contains('d-none')).toBe(true);
            checkboxCells.forEach(cell => {
                expect(cell.classList.contains('d-none')).toBe(true);
                const cb = cell.querySelector<HTMLInputElement>('input[type="checkbox"]');
                expect(cb?.checked).toBe(false);
            });
        });
    });

    // ── 3. Delete button ──────────────────────────────────────────────────────

    describe('Delete button', () => {
        it('shows the modal when at least one checkbox is ticked', () => {
            const editBtn = document.getElementById('edit-playlists-btn')!;
            const deleteBtn = document.getElementById('delete-playlists-btn')!;
            const checkboxCells = document.querySelectorAll<HTMLElement>('.playlist-checkbox-cell');

            editBtn.click();
            checkboxCells[0].querySelector<HTMLInputElement>('input[type="checkbox"]')!.checked = true;
            deleteBtn.click();

            expect(mockShow).toHaveBeenCalledTimes(1);
        });

        it('shows the modal even when no checkboxes are ticked', () => {
            const editBtn = document.getElementById('edit-playlists-btn')!;
            const deleteBtn = document.getElementById('delete-playlists-btn')!;

            editBtn.click();
            deleteBtn.click();

            expect(mockShow).toHaveBeenCalledTimes(1);
        });
    });

    // ── 4. Confirm delete ─────────────────────────────────────────────────────

    describe('Confirm delete button', () => {
        it('sends a DELETE request with the correct payload and headers', async () => {
            mockFetch.mockResolvedValueOnce({
                json: async () => ({ success: true, deleted_count: 1 }),
            });

            const editBtn = document.getElementById('edit-playlists-btn')!;
            const deleteBtn = document.getElementById('delete-playlists-btn')!;
            const confirmDeleteBtn = document.getElementById('confirm-delete-btn')!;
            const checkboxCells = document.querySelectorAll<HTMLElement>('.playlist-checkbox-cell');

            editBtn.click();
            checkboxCells[0].querySelector<HTMLInputElement>('input[type="checkbox"]')!.checked = true;
            deleteBtn.click();
            confirmDeleteBtn.click();

            await vi.waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(1));

            const [url, options] = mockFetch.mock.calls[0];
            expect(url).toContain('/your_playlists/delete_playlists');
            expect(options.method).toBe('DELETE');
            expect(options.headers['Content-Type']).toBe('application/json');
            expect(options.headers['X-CSRFToken']).toBe('testcsrftoken123');
            expect(JSON.parse(options.body)).toEqual({ playlist_id: [1] });
        });

        it('hides the modal and reloads the page on success', async () => {
            mockFetch.mockResolvedValueOnce({
                json: async () => ({ success: true, deleted_count: 1 }),
            });

            const reloadMock = vi.fn();
            vi.stubGlobal('location', {
                ...window.location,
                pathname: '/simple_john/your_playlists/',
                reload: reloadMock,
            });

            const editBtn = document.getElementById('edit-playlists-btn')!;
            const deleteBtn = document.getElementById('delete-playlists-btn')!;
            const confirmDeleteBtn = document.getElementById('confirm-delete-btn')!;
            const checkboxCells = document.querySelectorAll<HTMLElement>('.playlist-checkbox-cell');

            editBtn.click();
            checkboxCells[0].querySelector<HTMLInputElement>('input[type="checkbox"]')!.checked = true;
            deleteBtn.click();
            confirmDeleteBtn.click();

            await vi.waitFor(() => expect(reloadMock).toHaveBeenCalledTimes(1));
            expect(mockHide).toHaveBeenCalledTimes(1);
        });

        it('does not reload the page on a failed response', async () => {
            mockFetch.mockResolvedValueOnce({
                json: async () => ({ success: false }),
            });

            const reloadMock = vi.fn();
            vi.stubGlobal('location', {
                ...window.location,
                pathname: '/simple_john/your_playlists/',
                reload: reloadMock,
            });

            const editBtn = document.getElementById('edit-playlists-btn')!;
            const deleteBtn = document.getElementById('delete-playlists-btn')!;
            const confirmDeleteBtn = document.getElementById('confirm-delete-btn')!;

            editBtn.click();
            deleteBtn.click();
            confirmDeleteBtn.click();

            await vi.waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(1));
            expect(reloadMock).not.toHaveBeenCalled();
        });
    });
});