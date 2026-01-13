Process
* All good software is built incrementally:
    * Start with the smallest app/website possible, with just one feature.
        * For example, ‘the user can now sign in’. Build the back-end DB schema, the front-end framework and the two HTML pages.
        * Next, add one user action, ‘they can create a playlist’, repeat a similar process.
            * Post tune of the day/week
        * And so on.
    * The reason for doing this:
        * Very rarely is it practical to build all of the back-end first then immediately after building the front-end.
        * If you try to plan the whole thing and spend months building pieces, there’s basically no chance it will all work when you put it together. It’s far more productive to build pieces at a time. 
        * Your initial design ideas will never be perfect. The sooner you build it and try it out, the sooner you’ll figure out what works and what doesn’t, so you can make changes.
        * This way you always have a working app. Every day it gets better. You’re not wasting any time building something you might not use.
        * Keep the visual design straight-forward, don’t try to perfect it at the start as you’re guaranteed to forget things. 
        * Only after it’s functionally working perfectly does it make sense to polish the design.
    * In summary:
        * Build a feature first
        * Make it work second
        * Make it look pretty last


* MVP:
    * Note:
        * Refer to 'Consolidated features/actions' for full list + break down
    * First edition:
        * Start-up features
            * User can:
                * Sign-up
                    * Username + password
                * Sign in.
                * Create a profile
                    * Think about what fields
                * Receive an authentication email
                * Reset their password

        * Cataloguing:
            * The user can:
                * Create playlists/folders to categorise music.
                * Delete playlist/folder
                * Update playlists/folder:
                    * Add line
                    * Remove line
    
    * Second edition:
        * Social aspects:
            * Users can:
                * Search friends/people
                * Follow friends/people
                * View other friends profile(s)
                * Post music
                    * Include tags
                    * Which platforms first?
                * SCroll their feed
                
        * Cataloguing:
            * The user can make a playlist/folder public or private.

    * Third edition:
        * Social aspects:
            * Users can:
                * Like posts on their feed.
                    * The likes will be hidden.
                * Add 'tune of the week tag'
                * Collaborate on playlists
                * Post remaining music platforms
                * Posts links to Artists profiles, record labels or parties.
                * Post what they're selling on Discogs
        
        * Cataloguing:
            * users can:
                * have a liked/favourites playlist/folder.
                * Search the liked/favourites playlist/folder.


* Tech stack:
    * Back-end framework: Django
    * DB: ??
        * Do some research on this.
        * Can always ask Lewis and/or Ash
        * Brad could also be a good person to ask
    * Front-end: TypeScript, with CSS + HTML
    * Dockerise
    * Azure


* Data Engineering/Storage:
    * Research costs for hosting on Azure
    - How much storage is required just for links + texts, user details
    - Will there be images posted?
        - Research all of the above.


* Cost:
    * Research the costs via chatGPT.
        * Specifically storage and hosting costs.


Work items:
- Create free figma account

- Design:
    - Figma:
        - Create app flow
        - Wire frames
        - DB schema
            - split all of the above out for each of the MVP's.
            - Potentially just do it one MVP at a time.
- Dev:
    - Sprint 1:
        - Create Models:
            - UserModel
                - userID
                - Name = models.Charfield
                - Username = models.Charfield
                - Email = models.Charfield
                - Password = ?
                - emailed_verified = models.BooleanField
            - Folder:
                - folderID
                - folderName = models.Charfield
                - deleted = models.BooleanField
                - date_created = models.DateTimeField
                - FK = userID
            - folderTrack
                - trackID
                - Song title = models.Charfield(non-nullable)
                - Artist = models.Charfield(non-nullable)
                - Album = models.Charfield(nullable)
                - Record label = models.Charfield(nullable)
                - SouncloudPage = models.Charfield(nullable)
                - Where to buy = models.URLField(nullable)
                - Link = models.URLField(non-nullable)
                - Date_added = models.DateTimeField(non-nullable)
                - FK = folderID
                - MVP_2 features:
                    - Is deleted - non-nullable
                    - Public/Private - non-nullable
                        - This feature to be added later.
                - Note:
                    - Think how best to structure this, as the user can create many playlists, with many songs.
                        - That is, does there need to be model for the high-level fields of the playlist, then another model for the
                        tracks/mixes that are in the model.

        - Create Forms:
            - Sign-up
            - Sign-in
            - Reset password
            - Create profile
            - Create playlist

        - Views:
            - Homepage
            - Sign-up page
                - Send authentication email
            - Successful authentication page
            - Successful reset of password
                - Could combine these two.
            - Oops page :(
            - Create profile
            - Login
            - Create playlist
            - Edit playlist
            - Delete playlist

        - Templates:
            - HTML
                - Homepage
                - Sign-up
                - Login 
                - Successful authentication
            - Emails:
                - Authentication
                - Reset password

        - TypeScript:
            - To handle the following front-end functionalities:
                - Loading pop-up
                - Plus/minus buttons for the playlist
                - Pop-up: "Are you sure you want to delete that"
                - Playlists
                    - Want to avoid things being laggy like they are with AAWW

        - Basic CSS:
            - Look more into this.
                - Could I just copy 

        - Testing:
            - Unit tests
                - Django:
                    - Do this for every model
                - back-end
                - front-end 
                    - Will need to research how these are done.
            - Functional testing Docker
            - User testing

    - Once sprint 1 is done, look at the envrionment.YML and suss what packages are irrelevant and then update accordingly.

Consolidated features/actions:
- Starting-up features:
    - Users can sign up
        - Username
        - Password
            - Research how to store these things securely
    - Users can create a profile
        - Probably can leverage some fields from the sign-up form
    - Users can sign in
        - Username + password
    - User receives authentication email
        - Research the process for this
    - User can reset password

- Cataloguing:
    - User can create playlist/folder
        - Playlist/folder name:
            - Song name
            - Artists
            - Album
            - Record label
            - Platform:
                - YouTube
                - Bandcamp
                - Soundcloud
                - Spotify
                    - Do Spotfify last as they are cunts.
                - Nina
            - Link to song/mix
            - Where to buy
                - Good for public playlists as gives as much exposer to the artist as possible
            - Date added
            - Note:
                - For the intial MVP 
                - Emulate the feel of rekordbox
            - Question:
                - What is the best way to automatically populate the song/mix info from the link.
                - Research API's for each platform.  
    - User can search through the specific playlist.
    - User can update playlist/folder
        - Add line
        - Remove line
            - These can be made private or public
    - User can delete the playlist
    - Users have a 'liked/favorites' folder/playlist
        - Secondary feature are the search bar. 

- Social aspects:
    - Users can search for other users (friends/people)
    - Users can add people
    - Post links to:
        - songs/mixes/albums
            - Do this first
            - Include a link of where to buy
                - This can be Discogs, Bandcamp, Nina, Juno records
        - Playlists
        - record labels
            - Selling records on Discogs as well
        - artists
        - parties/festivals
            - Do the rest of these later
        - Add tags like in Soundcloud
            - Also research how Nina do it.
            - tune of the week tag d-.-b
    - Users can scroll their feed
        - Leverage other music apps, like Nina & Soundcloud
            - Nina has the coolest front-end
    - Users can like posts on their feed.
        - Keep the likes hidden, akin to what Soundcloud does now.
        - This feature won't be pushed to PROD until the 'hidden likes' is figured out. 
    - Users can view other's profile
        - this is a feature for last
    - Inbox
        - Users can message each other privately.
    - Users can collaborate on playlists together.
        - Think of how useful this would be for Ando's and I's tune of the week.