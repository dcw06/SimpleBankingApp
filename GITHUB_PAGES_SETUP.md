# GitHub Pages Deployment Guide

## Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named: **`SimpleBankingApp`** (or any name you prefer)
3. Set it to **Public** (required for free GitHub Pages)
4. Do NOT initialize with README, .gitignore, or license yet
5. Click "Create repository"

## Step 2: Push Your Code to GitHub

In your local terminal:

```bash
cd /Users/dcw06/Desktop/BankingApp

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: SimpleBankingApp with banking features, Google OAuth, and Plaid integration"

# Add remote repository (replace dcw06 with your GitHub username)
git remote add origin https://github.com/dcw06/SimpleBankingApp.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Enable GitHub Pages

1. Go to your GitHub repository: https://github.com/dcw06/SimpleBankingApp
2. Click **Settings** (top right)
3. Scroll down to **Pages** (left sidebar)
4. Under "Build and deployment":
   - Source: Select **Deploy from a branch**
   - Branch: Select **main** → **/ (root)**
   - Click **Save**

5. GitHub will show you: `Your site is live at https://dcw06.github.io/SimpleBankingApp/`

✅ Your website is now live! Test it here: https://dcw06.github.io/SimpleBankingApp/

## Step 4: (Optional) Point Custom Domain to GitHub Pages

Once you buy `simplebankingapp.com`:

### Option A: Using GitHub's Domain Setup (Easiest)

1. Go to your repo **Settings → Pages**
2. Under "Custom domain", enter: `simplebankingapp.com`
3. GitHub will ask you to verify DNS ownership

### Option B: Manual DNS Configuration (For GoDaddy, Namecheap, etc.)

1. Buy domain at GoDaddy, Namecheap, or similar
2. Go to your domain registrar's DNS settings
3. Add **CNAME record**:
   ```
   Host: @  (or leave blank)
   Type: ALIAS/ANAME
   Value: dcw06.github.io
   ```
   
4. OR add **A records** (if CNAME not available):
   ```
   Host: @
   Type: A
   Value: 185.199.108.153
   Value: 185.199.109.153
   Value: 185.199.110.153
   Value: 185.199.111.153
   ```

5. Go back to repo **Settings → Pages** and enter `simplebankingapp.com`
6. Check **Enforce HTTPS**
7. Wait 5-10 minutes for DNS to propagate

✅ Now `https://simplebankingapp.com` will point to your GitHub Pages site!

## File Structure

Your website files should be in `/website/` folder:

```
/website/
├── index.html          (Main landing page - already created)
├── style.css          (Styling - already created)
├── privacy.html       (Privacy Policy - create next)
└── terms.html         (Terms of Service - create next)
```

## Update Files Going Forward

Each time you update the website:

```bash
cd /Users/dcw06/Desktop/BankingApp

# Make changes to files in /website/ folder

git add website/
git commit -m "Update website content"
git push origin main
```

Changes go live instantly!

## Managing App Downloads

### Option 1: Direct GitHub Release

1. Go to your repo
2. Click "Releases" (right sidebar)
3. Click "Create a new release"
4. Upload `SimpleBankingApp.app` as a file attachment
5. Update `index.html` with the download link

### Option 2: Store on Web Host

If the .app file is too large (>100MB):
- Use AWS S3, Dropbox, or similar
- Update the download link in `index.html`

## DNS Records for WeChat Verification

When applying for WeChat integration, provide:
- **Domain**: simplebankingapp.com
- **Website URL**: https://simplebankingapp.com
- **Privacy Policy**: https://simplebankingapp.com/privacy.html
- **Terms**: https://simplebankingapp.com/terms.html

WeChat will visit your site to verify legitimacy.

## Troubleshooting

**"Page not found" after enabling Pages:**
- Wait 5-10 minutes for GitHub to build the site
- Check that files are in the root folder (or `/docs` subfolder if you configured that)

**Custom domain not working:**
- Check DNS records are propagated: https://dnschecker.org
- Wait up to 48 hours for global DNS propagation
- Ensure HTTPS is enabled in repo Settings

**Want to use a different folder:**
- Create `/docs` folder instead of `/website`
- In Settings → Pages, select **Deploy from a branch → /docs**

## Need Help?

- GitHub Pages docs: https://docs.github.com/en/pages
- DNS troubleshooting: https://dnschecker.org
- DNS propagation checker: https://whatsmydns.net
