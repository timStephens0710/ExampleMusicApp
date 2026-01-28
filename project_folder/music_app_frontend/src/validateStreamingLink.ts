//Create functions
export function getHostname(streamingLink: string): string | null {
    //Check for empty input
    if (!streamingLink) {
        return null;
    }

    //Clean the input
    const cleanedStreamingLink = streamingLink.trim();

    //Parse URL
    const url = URL.parse(cleanedStreamingLink);

    //Return hostname if URL is valid
    return url?.hostname ?? null;
}

//validateStreamingLink
export function checkStreamingLinkIsValid(hostName: string | null): null | string {
    //Check if hostName is null or empty
    if (!hostName) {
        return "The streaming link is empty. Please submit a valid link.";
    }

    //Normalize: remove 'www.' prefix and convert to lowercase
    const normalized = hostName.toLowerCase().replace(/^www\./, '');

    //Exact domain matches
    const exactDomains = [
        'youtube.com',
        'youtu.be',
        'music.youtube.com',
        'm.youtube.com',
        'bandcamp.com' // Main bandcamp site
    ];

    //Pattern matches for subdomains
    const domainPatterns = [
        /\.bandcamp\.com$/, //Matches artist.bandcamp.com, label.bandcamp.com
        //TODO: Add patterns for soundcloud, nina
    ];

    //Check exact matches
    if (exactDomains.includes(normalized)) {
        return null;
    }

    //Check pattern matches
    if (domainPatterns.some(pattern => pattern.test(normalized))) {
        return null;
    }

    return "The streaming link doesn't contain one of the supported platforms. Please submit a link from either YouTube or Bandcamp.";
}


//orchestrateCheckStreamingLinkIsValid function
export function orchestrateCheckStreamingLinkIsValid(streamingLink: string | null): string | null {
    //Check if streamingLink is null
    if(!streamingLink) {
        return 'The streaming link you have submitted is not valid. Please submit a valid link.'
    };
    
    //Get hostname
    const hostName = getHostname(streamingLink);
    
    //Check hostName is a supported platform 
    return checkStreamingLinkIsValid(hostName);
};


//Integrate into HTML page + Django form
document.addEventListener("DOMContentLoaded", (): void => {
    //Define const variables
    const form = document.getElementById("auth-form") as HTMLFormElement;
    const streamingLinkInput = document.getElementById("id_streaming_link") as HTMLInputElement;
    const streamlingLinkError = document.getElementById("streaming-link-error") as HTMLDivElement;

    //Check that all const exist
    if (!form || !streamingLinkInput || !streamlingLinkError) {
        console.warn("Required elements not found:", {
            form: !!form,
            streamingLinkInput: !!streamingLinkInput,
            streamlingLinkError: !!streamlingLinkError
        });
        return;
    }

    //Perform validation on form once user clicks "submit"
    form.addEventListener("submit", (event: SubmitEvent) => {
        const error = orchestrateCheckStreamingLinkIsValid(streamingLinkInput.value);

        if (error) {
            event.preventDefault(); //stop the Django form submission
            streamlingLinkError.textContent = error;
        } else {
            streamlingLinkError.textContent = "";
        }
    });
})

//check streaming plaform
export function supportedStreamingPlatformIsSelected(formDropDown: string): string[] {
    const supportedPlatforms = [
        "youtube",
        "youtube_music",
        "bandcamp",
    ];

    if (!supportedPlatforms.includes(formDropDown)) {
        return ["Please select a supported platform from the options below."];
    }

    return [];
}


//validateAddTrackForm
export function initValidateAddTrackForm(): void {
    const form = document.getElementById("auth-form") as HTMLFormElement | null;
    const streamingPlatformInput =
        document.getElementById("id_streaming_platform") as HTMLSelectElement | null;
    const streamingPlatformError =
        document.getElementById("streaming-platform-error") as HTMLDivElement | null;

    if (!form || !streamingPlatformInput || !streamingPlatformError) {
        console.warn("Critical form elements not found");
        return;
    }

    form.addEventListener("submit", (event: SubmitEvent): void => {
        console.log("TS submit handler fired");
        const errors = supportedStreamingPlatformIsSelected(
            streamingPlatformInput.value
        );

        console.log("Streaming platform value:", streamingPlatformInput.value);
        console.log("Errors:", errors);

        if (errors.length > 0) {
            event.preventDefault();
            console.log("Preventing submission");
            streamingPlatformError.textContent = errors[0];
        } else {
            streamingPlatformError.textContent = "";
        }
    });
    
};


console.log("validateStreamingLink initialized")
