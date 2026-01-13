import { describe, it, expect, beforeEach, vi } from "vitest";
import * as validateAddTrackForm from '../src/validateAddTrackForm'

//Test checkIsNull function
describe('checkIsNull', () => {
    it('returns null when the formText is not null', () => {
        expect(validateAddTrackForm.checkIsNull('hello world')).toBeNull();  
    });

    it('returns informative error message when formText is null', () => {
        expect(validateAddTrackForm.checkIsNull('')).toBe(
            'This field is mandatory, it cannot be empty.'
        );
    });
});

//Test checkLength250
describe('checkLength250', () => {
    it('returns null when the formText < 250 ', () => {
        expect(validateAddTrackForm.checkLength250('hello world')).toBeNull();  
    });

    it('returns informative error message when formText > 250 ', () => {
        expect(validateAddTrackForm.checkLength250('aZ9$kL2mQ#T7r@X8!WcE^YB0N%pHfJ&U*R1S+_e3t5oM~VdI=O4xqC6iP(h)lK{F}j-A|w:zG?u,.y<[]>/aZ9$kL2mQ#T7r@X8!WcE^YB0N%pHfJ&U*R1S+_e3t5oM~VdI=O4xqC6iP(h)lK{F}j-A|w:zG?u,.y<[]>/aZ9$kL2mQ#T7r@X8!WcE^YB0N%pHfJ&U*R1S+_e3t5oM~VdI=O4xqC6iP(h)lK{F}j-A|w:zG?u,.y<[]>/toolong')).toBe(
            "This text is too long, please ensure it's length is less than 250 characters."
        );
    });
});

//Test supportedStreamingPlatformIsSelected
describe('supportedStreamingPlatformIsSelected', () => {
    it('returns null when a supported streaming platform is selected', () => {
        expect(validateAddTrackForm.supportedStreamingPlatformIsSelected('YouTube')).toBeNull();
    });

    it('returns an informative message when a streaming platform has not been selected', () => {
        expect(validateAddTrackForm.supportedStreamingPlatformIsSelected('Soundcloud')).toBe(
            "Please select a supported platform from the options below"
        );
    });
});

//Test orchestrateCheckFormText
describe('orchestrateCheckFormText', () => {
    it('returns null when formText is not null & less than 250 characters', () => {
        const errorMessage = validateAddTrackForm.orchestrateCheckFormText('hello world')
        expect(errorMessage).toBeNull();
    });

    it('returns informative message when formText is null', () => {
        const errorMessage = validateAddTrackForm.orchestrateCheckFormText('')
        expect(errorMessage).not.toBeNull;
        expect(errorMessage).toBe(
            "This field is mandatory, it cannot be empty."
        );
    });

    it('returns informative message when formText is too long', () => {
        const errorMessage = validateAddTrackForm.orchestrateCheckFormText('aZ9$kL2mQ#T7r@X8!WcE^YB0N%pHfJ&U*R1S+_e3t5oM~VdI=O4xqC6iP(h)lK{F}j-A|w:zG?u,.y<[]>/aZ9$kL2mQ#T7r@X8!WcE^YB0N%pHfJ&U*R1S+_e3t5oM~VdI=O4xqC6iP(h)lK{F}j-A|w:zG?u,.y<[]>/aZ9$kL2mQ#T7r@X8!WcE^YB0N%pHfJ&U*R1S+_e3t5oM~VdI=O4xqC6iP(h)lK{F}j-A|w:zG?u,.y<[]>/toolong')
        expect(errorMessage).toBe(
            "This text is too long, please ensure it's length is less than 250 characters."
        )
    });
});

//Test checkStreamingPlatform