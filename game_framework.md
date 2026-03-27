https://chatgpt.com/c/683fa48e-fe00-8007-9707-4adaa69589f7

# 🧠 Agent Design: GAME Framework

## 🎯 Goals

### What to achieve:

1.  Identify potential enhancements to the codebase.
2.  Ensure enhancements are helpful and relevant.
3.  Keep enhancements small and self-contained for low-risk
    implementation.
4.  Ensure no breaking changes to existing interfaces.
5.  Only implement features the user explicitly approves.

### How to achieve it:

-   Randomly pick a file in the codebase and read it.
-   Explore related files (max 5 files total).
-   Propose 3 feature ideas that:
    -   Can be implemented with 2--3 functions
    -   Require minimal editing
-   Ask the user to choose one feature.
-   List files to be edited and proposed changes.
-   Implement changes file by file.

## 🛠 Actions

-   list_project_files()
-   read_project_file(file_path)
-   ask_user_to_select_feature(options)
-   edit_project_file(file_path, changes)

## 🧠 Memory

-   Store file contents in conversation
-   Track user decisions
-   Track proposed and approved changes

## 🌐 Environment

-   Runs locally using Python
-   Can later be adapted to GitHub Actions or CI/CD
