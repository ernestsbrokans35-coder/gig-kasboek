# Gig Kasboek

Freelance books on your phone: invoices from your email, VAT per quarter with the filing deadline, hours, earnings, expenses with receipt photos. It is a plain web app that installs to the home screen. There is no server and no AI behind it: everything runs in the phone's browser and all data stays on that device.

## Folders

- `app/` is the app itself. These files are what gets hosted.
- `src/` is the source. After changing `src/index.src.html` or `src/parse.js`, run `py src/build.py` to rebuild `app/index.html`.
- `artifact/` is the first version, which runs inside Claude. Its stylesheet is reused by the build.

## What works without any setup

Open `app/index.html` from any web host. Add invoice PDFs by hand under Invoices, add expenses, save backups.

## Switching on the email connection

The app reads Gmail directly from the phone, read-only, and looks only for PDFs from the sender addresses the user enters under Setup.

1. Host the `app/` folder on an https address (GitHub Pages, Cloudflare Pages, Netlify).
2. In Google Cloud Console, create a project, enable the Gmail API, and set up the OAuth consent screen as External with the scope `.../auth/gmail.readonly`.
3. Create an OAuth client ID of type "Web application". Add the hosted address as an authorised JavaScript origin, and the full app address (ending in `/`) as an authorised redirect URI.
4. Paste the client ID into `app/config.js`. It is not a secret.
5. While the consent screen is in "Testing", add each user's Gmail address under Test users (100 at most). They see a "Google hasn't verified this app" screen once.

## Known limits

- The app checks email when it is opened or brought back to the front. It cannot check while it is closed.
- Google's permission lasts about an hour. After that the Check email button sends the user through Google's screen again, usually one tap.
- Opening the app to the public needs Google's verification for Gmail access, which includes a paid yearly security assessment. The way around that is a small server that users forward their invoice emails to.
- Invoices in the Clevergig layout are read in full (shifts, hours, VAT). Other layouts get a best-effort total and VAT, are flagged "check the numbers", and can be corrected by hand.
- Data lives only on the device. Use Setup, Save a backup.
