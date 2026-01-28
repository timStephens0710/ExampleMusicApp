/*
 * Add Dynamic changing of form fields for the 'add_track' form
 * If the user selects 'mix' for track_type:
 *      - The following fields will be hidden:
 *          - album_name
 *          - record_label
 *          - purchase_link
 *      - The following fields will have the display name changed:
 *          - track_name: mix_name 
 */

function initializeTrackForm(): void {
    const form = document.getElementById("auth-form") as HTMLFormElement;
    const trackTypeInput = document.getElementById("id_track_type") as HTMLInputElement;
    const trackNameLabel = document.querySelector('label[for="id_track_name"]') as HTMLLabelElement;

    // Check key elements aren't null 
    if (!form || !trackTypeInput || !trackNameLabel) {
        console.warn('Required element not found');
        return;
    }

    const mixPageContainer = document.getElementById("div_id_mix_page") as HTMLDivElement | null;
    const albumNameContainer = document.getElementById("div_id_album_name") as HTMLDivElement | null;
    const recordLabelContainer = document.getElementById("div_id_record_label") as HTMLDivElement | null;
    const purchaseLinkContainer = document.getElementById("div_id_purchase_link") as HTMLDivElement | null;

    function updateFormForTrackType(): void {
        const isTrack = trackTypeInput.value === "track";

        if (isTrack) {
            trackNameLabel.textContent = "Track Name";

            mixPageContainer?.style.setProperty('display', 'none');
            albumNameContainer?.style.removeProperty('display');
            recordLabelContainer?.style.removeProperty('display');
            purchaseLinkContainer?.style.removeProperty('display');
        } else {
            trackNameLabel.textContent = "Mix Name";

            mixPageContainer?.style.removeProperty('display');
            albumNameContainer?.style.setProperty('display', 'none');
            recordLabelContainer?.style.setProperty('display', 'none');
            purchaseLinkContainer?.style.setProperty('display', 'none');
        }
    }

    //Run once on initialization (for pre-filled value)
    updateFormForTrackType();

    //Run when/if the user changes it
    trackTypeInput.addEventListener('change', updateFormForTrackType);
    console.log('dynamic add track form initialized');
}

//Try immediately when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTrackForm);
} else {
    initializeTrackForm();
}

//Fallback: wait for the form to appear
const observer = new MutationObserver((mutations, obs) => {
    const form = document.getElementById("auth-form");
    if (form) {
        console.log('Form detected via MutationObserver');
        initializeTrackForm();
        obs.disconnect(); // Stop observing once found
    }
});

//Start observing when DOM is ready
if (document.body) {
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
} else {
    document.addEventListener('DOMContentLoaded', () => {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}