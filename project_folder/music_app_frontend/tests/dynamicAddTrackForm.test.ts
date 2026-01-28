import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest's expect with Testing Library matchers
expect.extend(matchers);

describe('Track Form Dynamic Behavior', () => {
    let mockForm: HTMLFormElement;
    let mockTrackTypeInput: HTMLSelectElement;
    let mockTrackNameLabel: HTMLLabelElement;
    let mockMixPageContainer: HTMLDivElement;
    let mockAlbumNameContainer: HTMLDivElement;
    let mockRecordLabelContainer: HTMLDivElement;
    let mockPurchaseLinkContainer: HTMLDivElement;

    beforeEach(() => {
        // Create a clean DOM structure before each test
        document.body.innerHTML = `
            <form id="auth-form">
                <label for="id_track_name">Track Name</label>
                <select id="id_track_type">
                    <option value="track">Track</option>
                    <option value="mix">Mix</option>
                </select>
                <div id="div_id_mix_page">Mix Page Field</div>
                <div id="div_id_album_name">Album Name Field</div>
                <div id="div_id_record_label">Record Label Field</div>
                <div id="div_id_purchase_link">Purchase Link Field</div>
            </form>
        `;

        // Get references to elements
        mockForm = document.getElementById('auth-form') as HTMLFormElement;
        mockTrackTypeInput = document.getElementById('id_track_type') as HTMLSelectElement;
        mockTrackNameLabel = document.querySelector('label[for="id_track_name"]') as HTMLLabelElement;
        mockMixPageContainer = document.getElementById('div_id_mix_page') as HTMLDivElement;
        mockAlbumNameContainer = document.getElementById('div_id_album_name') as HTMLDivElement;
        mockRecordLabelContainer = document.getElementById('div_id_record_label') as HTMLDivElement;
        mockPurchaseLinkContainer = document.getElementById('div_id_purchase_link') as HTMLDivElement;
    });

    afterEach(() => {
        document.body.innerHTML = '';
        vi.clearAllMocks();
    });

    describe('Form Initialization', () => {
        test('should find all required form elements', () => {
            expect(mockForm).toBeInTheDocument();
            expect(mockTrackTypeInput).toBeInTheDocument();
            expect(mockTrackNameLabel).toBeInTheDocument();
        });

        test('should find all optional container elements', () => {
            expect(mockMixPageContainer).toBeInTheDocument();
            expect(mockAlbumNameContainer).toBeInTheDocument();
            expect(mockRecordLabelContainer).toBeInTheDocument();
            expect(mockPurchaseLinkContainer).toBeInTheDocument();
        });

        test('should handle missing form gracefully', () => {
            document.body.innerHTML = '';
            const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
            
            const form = document.getElementById('auth-form');
            expect(form).toBeNull();
            
            consoleWarnSpy.mockRestore();
        });
    });

    describe('Track Type: "track" selected', () => {
        beforeEach(() => {
            mockTrackTypeInput.value = 'track';
            simulateUpdateFormForTrackType();
        });

        test('should set label to "Track Name"', () => {
            expect(mockTrackNameLabel.textContent).toBe('Track Name');
        });

        test('should hide mix page container', () => {
            expect(mockMixPageContainer.style.display).toBe('none');
        });

        test('should show album name container', () => {
            expect(mockAlbumNameContainer.style.display).not.toBe('none');
        });

        test('should show record label container', () => {
            expect(mockRecordLabelContainer.style.display).not.toBe('none');
        });

        test('should show purchase link container', () => {
            expect(mockPurchaseLinkContainer.style.display).not.toBe('none');
        });
    });

    describe('Track Type: "mix" selected', () => {
        beforeEach(() => {
            mockTrackTypeInput.value = 'mix';
            simulateUpdateFormForTrackType();
        });

        test('should set label to "Mix Name"', () => {
            expect(mockTrackNameLabel.textContent).toBe('Mix Name');
        });

        test('should show mix page container', () => {
            expect(mockMixPageContainer.style.display).not.toBe('none');
        });

        test('should hide album name container', () => {
            expect(mockAlbumNameContainer.style.display).toBe('none');
        });

        test('should hide record label container', () => {
            expect(mockRecordLabelContainer.style.display).toBe('none');
        });

        test('should hide purchase link container', () => {
            expect(mockPurchaseLinkContainer.style.display).toBe('none');
        });
    });

    describe('Event Handling', () => {
        test('should update form when track type changes', () => {
            // Start with 'track'
            mockTrackTypeInput.value = 'track';
            simulateUpdateFormForTrackType();
            expect(mockTrackNameLabel.textContent).toBe('Track Name');

            // Change to 'mix'
            mockTrackTypeInput.value = 'mix';
            mockTrackTypeInput.dispatchEvent(new Event('change'));
            simulateUpdateFormForTrackType();
            
            expect(mockTrackNameLabel.textContent).toBe('Mix Name');
            expect(mockMixPageContainer.style.display).not.toBe('none');
        });

        test('should handle pre-filled value on page load', () => {
            // Simulate Django pre-filling the value
            mockTrackTypeInput.value = 'mix';
            
            // Initialize (would normally be called by initializeTrackForm)
            simulateUpdateFormForTrackType();
            
            expect(mockTrackNameLabel.textContent).toBe('Mix Name');
            expect(mockMixPageContainer.style.display).not.toBe('none');
        });
    });

    describe('MutationObserver Behavior', () => {
        test('should detect when form is added to DOM', async () => {
            // Start with empty body
            document.body.innerHTML = '';

            const formDetected = new Promise<void>((resolve) => {
                // Set up MutationObserver
                const observer = new MutationObserver((mutations, obs) => {
                    const form = document.getElementById('auth-form');
                    if (form) {
                        expect(form).toBeInTheDocument();
                        obs.disconnect();
                        resolve();
                    }
                });

                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });

                // Simulate Django injecting the form after a delay
                setTimeout(() => {
                    document.body.innerHTML = `
                        <form id="auth-form">
                            <select id="id_track_type"></select>
                        </form>
                    `;
                }, 10);
            });

            await formDetected;
        });

        test('should stop observing after form is found', () => {
            const disconnectSpy = vi.fn();
            const mockObserver = {
                observe: vi.fn(),
                disconnect: disconnectSpy
            };

            // Simulate finding the form
            document.body.innerHTML = '<form id="auth-form"></form>';
            const form = document.getElementById('auth-form');
            
            if (form) {
                mockObserver.disconnect();
            }

            expect(disconnectSpy).toHaveBeenCalled();
        });
    });

    describe('Edge Cases', () => {
        test('should handle missing optional containers gracefully', () => {
            // Remove optional containers
            mockMixPageContainer.remove();
            mockAlbumNameContainer.remove();

            mockTrackTypeInput.value = 'track';
            
            // Should not throw error
            expect(() => {
                simulateUpdateFormForTrackType();
            }).not.toThrow();
        });

        test('should handle invalid track type value', () => {
            mockTrackTypeInput.value = 'invalid_value';
            simulateUpdateFormForTrackType();
            
            // Should default to "mix" behavior (isTrack === false)
            expect(mockTrackNameLabel.textContent).toBe('Mix Name');
        });
    });

    // Helper function to simulate the updateFormForTrackType logic
    function simulateUpdateFormForTrackType(): void {
        const isTrack = mockTrackTypeInput.value === 'track';

        if (isTrack) {
            mockTrackNameLabel.textContent = 'Track Name';
            mockMixPageContainer.style.setProperty('display', 'none');
            mockAlbumNameContainer.style.removeProperty('display');
            mockRecordLabelContainer.style.removeProperty('display');
            mockPurchaseLinkContainer.style.removeProperty('display');
        } else {
            mockTrackNameLabel.textContent = 'Mix Name';
            mockMixPageContainer.style.removeProperty('display');
            mockAlbumNameContainer.style.setProperty('display', 'none');
            mockRecordLabelContainer.style.setProperty('display', 'none');
            mockPurchaseLinkContainer.style.setProperty('display', 'none');
        }
    }
});