---
name: github-sync
description: Automatically sync the current repository to GitHub by staging changes, creating commits, and pushing to remote.
---

# GitHub Sync Skill

## Purpose

This skill automates the git workflow to sync local changes to GitHub.

## Workflow

When triggered, this skill:
1. Stages all changes (`git add .`)
2. Creates a commit with a descriptive message
3. Pushes to the remote repository (`git push`)

## Usage

Mention "github update" in your message to trigger automatic syncing.

## Git Configuration

This repository is configured with:

- **Name**: jahody
- **Email**: <ajf.zlamal@gmail.com>

## Notes

- Ensure you have write access to the remote repository
- The skill will use your configured git credentials
- Commit messages are auto-generated based on changed files
- Git identity is set at repository level (not global)
