Contributing
============

Ask questions or report issues
------------------------------
Please direct all questions and bug reports to <a href="mailto:LIB.DL.repoteam@msu.edu">LIB.DL.repoteam@msu.edu</a>.

Submitting patches
------------------

**First time setup**  
Log into you GitHub account and then click the *Fork* button on the [Sandhill repository home page](https://github.com/MSU-Libraries/sandhill).


Install the required packages to setup Sandhill (note the required `sudo` privileges for these commands only):
```
sudo apt update
sudo apt install virtualenv python3-pip
```

Clone the Sandhill repository locally and navigate into that directory:  
```
git clone https://github.com/MSU-Libraries/sandhill.git
cd sandhill
```

Now add your fork as a new remote:
```
git remote add fork https://github.com/{username}/sandhill
```

Create a new branch for your changes:
```
git checkout -b your-branch-name
```

Next create a virtual environment and install the required [pip](https://pip.pypa.io/en/stable/quickstart/) packages:
```
virtualenv -p python3 env
env/bin/pip install -r requirements.txt
```

**Start coding**  
Make sure you have the latest sandhill code:
```
git fetch origin
```

Create a new branch for your changes off of the master branch:
```
git checkout -b your-branch-name origin/master
```
As you are writing your code, make sure you are following the [coding standards](docs/code-standards.md)
that Sandhill has defined.

Commit changes as you go to your forked branch:
```
git push -set-upstream fork your-branch-name
```

**Test your code**  
Before you submit a pull request you must make sure that all of your code has appropriate
tests written for them and have complete coverage. See the [testing steps](docs/development-guide.md#testing)
documentation for how to write and run unit tests.

```
env/bin/pytest
```

**Lint your code**  
The final step before submiting your changes is to run a lint check to identify basic style issues
for better code consistency throughout the repository.

```
env/bin/pylint sandhill/
```

**Submitting your code**  
Once you have completed all of the above steps you are ready to submit your pull request. Please follow
the [official GitHub documentation for pull requests](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).
But basically you can just go back to the [Sandhill repository](https://github.com/MSU-Libraries/sandhill.git) and click on
*Pull Request* and follow the prompts to submit it.
