interface userPlaylist {
    playlist_name: string;
    owner: string;
    playlist_type: "tracks" | "mixes" | "samples";
    description: string;
    is_private: "public" | "private";
    date_updated: Date;
}

interface playlistTrack {
    position: number;
    track_name: string;
    artist: string;
    album: string;
    link: URL;
    added_by: string;
    date_added: Date;
}