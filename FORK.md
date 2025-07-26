### Clone forked repository to local machine:

```bash
git clone https://github.com/vladimirpesic/juggler.git
```

### Navigate to the directory:

```bash
cd juggler
```

### Add the original repository as an upstream remote to fetch its updates:

```bash
git remote add upstream https://github.com/bytedance/trae-agent.git
```

### Verify the remotes:

```bash
git remote -v
```

You should see origin (your fork) and upstream (original repository).

### Create a new branch for new features and changes:

```bash
git checkout -b custom-tools
```

### Make changes, commit, and push to your fork:

```bash
git add .
git commit -m "Add new feature or improvement"
git push origin custom-tools
```

### Fetch updates from original repository:

```bash
git fetch upstream
```

### Merge updates into your local main branch:

```bash
git checkout main
git merge upstream/main
```

Resolve any merge conflicts if prompted (Git will guide you through conflict resolution).

### Push the updated main branch to your fork:

```bash
git push origin main
```

### To incorporate upstream changes into your feature branch, rebase it:

```bash
git checkout custom-tools
git rebase main
```

Resolve conflicts if any, then continue:

```bash
git rebase --continue
```

### To force-push the updated branch to your fork:

```bash
git push origin custom-tools --force
```

### Merge your changes:

To integrate your `custom-tools` branch into your fork’s main branch, create a pull request from `custom-tools` branch to main using GitHub’s interface.
Regularly sync with the original (upstream) repository.
Periodically repeat `git fetch upstream` to keep your fork’s main branch updated with the original repository’s changes.
