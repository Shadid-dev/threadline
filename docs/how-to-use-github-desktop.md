# How to use GitHub for this project (no experience needed)

This guide uses **GitHub Desktop**, an app with buttons, so you never need to type commands.
If you only want to upload a few files, the even simpler website method is in **Part 4**.

---

## Part 1: The five words you need

| Word | What it means here |
|---|---|
| **Repository (repo)** | The shared project folder. Ours is called `threadline`. |
| **Pull** | Download everyone else's latest changes to your laptop. |
| **Commit** | Save a snapshot of *your* changes on your laptop, with a short note saying what you did. |
| **Push** | Upload your commits so the team can see them. Committing alone does **not** share anything. |
| **main** | The one shared version of the project. We all work on `main` to keep things simple. |

---

## Part 2: One-time setup (about 15 minutes)

1. **Accept the invitation.** Check the email linked to your GitHub account for "Shadid-dev invited you to collaborate on threadline" and click **Accept**. (All four of you are already listed as collaborators. If you can't open https://github.com/Shadid-dev/threadline, tell Shadid.)
2. **Install GitHub Desktop** from https://desktop.github.com and sign in with your GitHub account.
3. **Download (clone) the project:** in GitHub Desktop choose **File → Clone Repository**, pick **Shadid-dev/threadline**, choose a place on your laptop (Documents is fine) and click **Clone**.
4. **Open it:** click **Show in Finder** (Mac) / **Show in Explorer** (Windows) to see the files, or **Open in Visual Studio Code**.

---

## Part 3: Every time you work (the routine)

**Before you start**

1. Open GitHub Desktop. Check that the top bar says **Current Repository: threadline** and **Current Branch: main**.
2. Click **Fetch origin**. If the button then says **Pull origin**, click it. You now have the latest files.

**Do your work**

3. Add or edit files in your own folder, `team/<your-name>_<your-agent>/`. You can simply drag files into that folder in Finder or Explorer.

**Share your work**

4. Go back to GitHub Desktop. The left panel lists every file you changed. **Read the list.** If you see a `.env` file or anything with a password or key in it, untick it.
5. Bottom left, in **Summary**, write a short note, for example: `Add my Lab 2 Narrator contract`.
6. Click **Commit to main**.
7. Click **Push origin** at the top. This is the step people forget. Until you push, nobody else can see your work.

Tip: do steps 4 to 7 at the end of every session, even if your work is half finished.

---

## Part 4: The website method (only uploading files)

1. Go to https://github.com/Shadid-dev/threadline and sign in.
2. Click into **team**, then into **your folder**.
3. Click **Add file → Upload files**, drag your files in, write a short note in the box at the bottom, and click **Commit changes**.

That's it; there's no push step on the website. Use GitHub Desktop for anything bigger than a few files.

---

## Part 5: What goes where

| You want to... | Put it in... |
|---|---|
| Share your Lab 2 / Lab 3 / Lab 4 work | `team/<your-folder>/labs/` |
| Write code for your agent | `team/<your-folder>/` first. When it works, we move it into the main prototype together. |
| Share notes or a document for everyone | `docs/` (tell the team in the group chat) |
| Change the shared prototype in `lab4/` | Ask in the group chat first, so two people don't edit the same file at once. |

---

## Part 6: When something goes wrong

| Message or problem | What to do |
|---|---|
| **"Push rejected"** or **"newer commits on remote"** | Click **Pull origin** first, then **Push origin** again. |
| **"Conflict"** | Two people changed the same lines. Don't panic and don't force anything. Screenshot it and post it in the group chat. |
| You can't see `threadline` in the clone list | You haven't accepted the invitation yet (Part 2, step 1). |
| You committed something by mistake but haven't pushed | In the **History** tab, right-click the commit and choose **Undo Commit**. |
| You pushed a password or API key | Tell Shadid immediately, then delete and recreate that key on the provider's website. Removing the file afterwards is not enough. |

Stuck for more than 20 minutes? Post a screenshot in the group chat.
