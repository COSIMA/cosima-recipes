Contributing to COSIMA Recipes
==============================

There are three main types of recipes, and we welcome contributions to any and
all of these:

Tutorials
   *Tutorials* are the most comprehensive kind of recipe. We intend for these
   to be an introduction to the `COSIMA Cookbook`_ and how to work with it,
   but not for it to document any scientific analysis.

Documented Examples
   For demonstrating scientific uses of the Cookbook, one of your options
   is to create a *documented example*. As the name suggests, these should be
   a high-quality, well-documented workflow. Ideally, these showcase
   best-practice uses of the Cookbook and other libraries such as `xarray`_.

Contributed Examples
   Of course, it can be a bit more effort to fully document your workflow,
   or you might not know the best practices. Instead of letting these poor
   notebooks languish, we welcome these as *contributed examples*! The noble
   goal would be for all of these to eventually be promoted to *documented
   examples*, but it is still better for them to be widely available so people
   don't have to constantly rediscover the same diagnostics.

.. _COSIMA Cookbook: https://github.com/COSIMA/cosima-cookbook
.. _xarray: https://xarray.dev/


Getting started with git
------------------------

Development of the COSIMA Recipes is coordinated through `GitHub`_, so you'll
need to know how to work with the distributed version control software git to
be able to contribute back. A good set of resources for getting started with
git and GitHub is available on the `ACCESS-NRI Training`_ portal.

.. _GitHub: https://github.com/COSIMA/cosima-recipes
.. _ACCESS-NRI Training: https://access-nri.github.io/Training/HowTos/GitAndGitHub/


Working on your recipe
----------------------

In most cases, you'll want to be working on your recipes directly on HPC
infrastructure, such as `NCI`_. In this case, you should be familiar with
`running COSIMA Recipes at NCI`_, and particularly with running `on the ARE`_.
These guides will take you through cloning the COSIMA Recipes repository and
working with notebooks to perform your analysis. Make use of git by *branching*
and *committing* (as described on the `GitHub git cheat sheet`_, for example).
You can interact with git through a terminal on your ARE session, or through a
direct connection to Gadi.

When you have developed your notebook to the point where you'd like to
contribute it to the main COSIMA Recipes repository, continue to the next
section. If you can't quite fully complete your notebook, you can seek advice
on the `ACCESS-Hive Forum`_, or submit it as a pull request anyway, asking for
feedback! Sometimes having more eyes on a problem can be useful, and other
people might not have to duplicate the full process if they can use your
notebook as a base.

.. _NCI: https://nci.org.au/
.. _running COSIMA Recipes at NCI: https://github.com/COSIMA/cosima-cookbook/wiki/Beginners-Guide-to-the-COSIMA-Cookbook#running-cosima-recipes-at-nci
.. _on the ARE: https://github.com/COSIMA/cosima-cookbook/wiki/How-to-use-COSIMA-Cookbook-on-the-ARE-@-NCI
.. _GitHub git cheat sheet: https://training.github.com/downloads/github-git-cheat-sheet/
.. _ACCESS-Hive Forum: https://forum.access-hive.org.au/


Submitting a Pull Request
-------------------------

Make sure you have staged and committed the changes to your notebook to your
local clone of COSIMA Recipes. You'll need to then synchronise these changes
to GitHub to be able to propose them in a Pull Request. If you haven't already,
`create a fork`_ of the COSIMA Recipes repository. Once you have pushed your
new branch onto your fork, you'll be able to `create a pull request`_.

.. _create a fork: https://docs.github.com/en/get-started/quickstart/fork-a-repo
.. _create a pull request: https://docs.github.com/en/get-started/quickstart/github-flow#create-a-pull-request


Reviewing existing Pull Requests
--------------------------------

Another very useful way to contribute to COSIMA Recipes is to review existing
Pull Requests. Even if you don't have a new workflow to propose to the world,
you might be an expert in some part of the process and your feedback is valuable!
Take a look at the `existing Pull Requests`_ to see if anything takes your fancy.
There are two ways to interact with these, depending on what sort of feedback
you'd like to provide.

Since the Pull Requests are the usual GitHub type, you can submit your review using
the standard GitHub interface. This amounts to leaving a comment on the changes
introduced by the commits. However, because notebooks contain a lot of extra
metadata and structure, it's not very pleasant to review them through a file diff!
Instead, the *review-notebook-app* bot will leave a comment with a **ReviewNB**
button on every Pull Request: this lets you leave your feedback on a representation
of the notebook itself.

.. _existing Pull Requests: https://github.com/COSIMA/cosima-recipes/pulls