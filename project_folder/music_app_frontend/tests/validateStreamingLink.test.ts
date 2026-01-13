import { describe, it, expect, beforeEach} from "vitest";
import  * as validateStreamingLink from '../src/validateStreamingLink'

//Test getHostname function
describe('getHostname', () => {
    it('returns hostname from a given url', () => {
        expect(validateStreamingLink.getHostname('https://www.youtube.com/watch?v=CaCSuzR4DwM')).toBe(
        "www.youtube.com"
        );
    });

    it('returns null for an invalid url', () => {
        expect(validateStreamingLink.getHostname('badurl.spent')).toBeNull();
    });

    it('returns null for an email address', () => {
        expect(validateStreamingLink.getHostname('my_email@gmail.com')).toBeNull();
    });

    it('trims the whitespaces effectively', () => {
        expect(validateStreamingLink.getHostname('    https://www.youtube.com/watch?v=CaCSuzR4DwM    ')).toBe(
        "www.youtube.com"
        );
    });
});


//Test checkStreamingLinkIsValid function
describe('checkStreamingLinkIsValid', () => {
    it('returns null when a YouTube url is submitted', () => {
        expect(validateStreamingLink.checkStreamingLinkIsValid('youtube.com')).toBeNull();
    });

    it('returns null when a BandCamp url is submitted', () => {
        expect(validateStreamingLink.checkStreamingLinkIsValid('bandcamp.com')).toBeNull();
    });

    it('returns informative message to user with an unsupported hostname', () => {
        expect(validateStreamingLink.checkStreamingLinkIsValid('soundcloud.com')).toBe(
            "The streaming link doesn't contain one of the supported platforms. Please submit a link from either YouTube or Bandcamp."
        );
    });

    it('returns informative message to user when hostname is null', () => {
        expect(validateStreamingLink.checkStreamingLinkIsValid(null)).toBe(
            "The streaming link is empty. Please submit a valid link."
        );
    });
});


//Test orchestrateCheckStreamingLinkIsValid function
describe('checkStreamingLinkIsValid', () => {
    it('returns null when a YouTube url is submitted', () => {
        const streamingLinkCheckMessage = validateStreamingLink.orchestrateCheckStreamingLinkIsValid('https://www.youtube.com/watch?v=CaCSuzR4DwM');
        expect(streamingLinkCheckMessage).toBeNull();
    });

    it('returns null when a BandCamp url is submitted', () => {
        const streamingLinkCheckMessage = validateStreamingLink.orchestrateCheckStreamingLinkIsValid('https://selfversedrecords.bandcamp.com/track/permanent-as-your-errors');
        expect(streamingLinkCheckMessage).toBeNull();
    });

    it('whitespaces work effictively', () => {
    const streamingLinkCheckMessage = validateStreamingLink.orchestrateCheckStreamingLinkIsValid('    https://www.youtube.com/watch?v=CaCSuzR4DwM    ');
    expect(streamingLinkCheckMessage).toBeNull();
    });

    it('returns an informating error message when the streaming link is null', () => {
        const streamingLinkCheckMessage = validateStreamingLink.orchestrateCheckStreamingLinkIsValid(null)
        expect(streamingLinkCheckMessage).not.toBeNull;
        expect(streamingLinkCheckMessage).toBe(
            'The streaming link you have submitted is not valid. Please submit a valid link.'
        );
    });

    it('returns an informating error message for an unsupported platform', () => {
        const streamingLinkCheckMessage = validateStreamingLink.orchestrateCheckStreamingLinkIsValid("https://soundcloud.com/edwinmusicchannel/edmix-144-purelink")
        expect(streamingLinkCheckMessage).not.toBeNull;
        expect(streamingLinkCheckMessage).toBe(
            "The streaming link doesn't contain one of the supported platforms. Please submit a link from either YouTube or Bandcamp."
        );
    });

    it('returns an informating error message for an edge case url', () => {
        const streamingLinkCheckMessage = validateStreamingLink.orchestrateCheckStreamingLinkIsValid("www.youtube@gmail.com")
        expect(streamingLinkCheckMessage).not.toBeNull;
        expect(streamingLinkCheckMessage).toBe(
            "The streaming link is empty. Please submit a valid link."       
        );
    });
});

//Test supportedStreamingPlatformIsSelected
describe('supportedStreamingPlatformIsSelected', () => {
    it('returns null when a supported streaming platform is selected', () => {
        expect(validateStreamingLink.supportedStreamingPlatformIsSelected('youtube')).toStrictEqual([]);
    });

    it('returns an informative message when a streaming platform has not been selected', () => {
        expect(validateStreamingLink.supportedStreamingPlatformIsSelected('Soundcloud')).toStrictEqual(
            ["Please select a supported platform from the options below.",]
        );
    });
});


//Test DOM integration
describe("validateAddTrackForm HTML integration", () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <form id="auth-form">
                <select id="id_streaming_platform">
                    <option value="">-----</option>
                    <option value="bandcamp">BandCamp</option>
                    <option value="youtube">YouTube</option>
                    <option value="youtube_music">YouTube Music</option>
                </select>
                <div id="streaming-platform-error"></div>
                <button type="submit">Submit</button>
            </form>
        `;

        validateStreamingLink.initValidateAddTrackForm(); //
    });

    it("prevents submit and shows error for unsupported platform", () => {
        const form = document.getElementById("auth-form") as HTMLFormElement;
        const select = document.getElementById("id_streaming_platform") as HTMLSelectElement;
        const errorDiv = document.getElementById("streaming-platform-error") as HTMLDivElement;

        select.value = "";

        const event = new Event("submit", { bubbles: true, cancelable: true });
        const prevented = !form.dispatchEvent(event);

        expect(prevented).toBe(true);
        expect(errorDiv.textContent).toContain("supported platform");
    });

    it("allows submit for supported platform", () => {
        const form = document.getElementById("auth-form") as HTMLFormElement;
        const select = document.getElementById("id_streaming_platform") as HTMLSelectElement;
        const errorDiv = document.getElementById("streaming-platform-error") as HTMLDivElement;

        select.value = "youtube";

        const event = new Event("submit", { bubbles: true, cancelable: true });
        const prevented = !form.dispatchEvent(event);

        expect(prevented).toBe(false);
        expect(errorDiv.textContent).toBe("");
    });
});