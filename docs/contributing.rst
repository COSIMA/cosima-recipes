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


Tips for making a good recipe
----------------------------

As researchers, we often develop code as part of our research and most of
the time the main aim of code development is to find answers to questions
that have not yet been explored. Reproducibility may not always be considered
as part of the code development process or be a priorty. If this is something
that resonates with you, or if you would like to learn more about making your
code shareable and reproducible, we are including some tips and good practices
to help you achieve this. 

1. Give the recipe a descriptive but generic title. Avoid being too specific
   as this will make it harder for other users to find code that matches their
   needs. For example, ``Computing pairwise distances between grid cells`` may be
   a better title than ``Computing distance between grid cells in the Southern
   Ocean and ice edge`` because the latter gives users the impression that
   the recipe is only relevant if they are looking at sea ice.

2. Include a short introduction summarising what your script is expected to
   do. You can include some information of the inputs needed to run your script,
   the expected outputs, and the methods you are using to get there. As with
   the title, we also recommend that you keep your description as generic as
   possible.

3. Give your variables and functions a descriptive name, so it is easy for
   users to read and follow your code. For example, ``mean_monthly_temperature_australia``
   is better than ``temp``.

4. Organising your recipe in smaller sections makes it easier for users to
   identify the part of your code that is relevant to them. 

5. Make sure you document your recipe well. Do not be afraid to provide a
   small description of what each section of your code does and why you are
   doing it. This tells the users the purpose of running a particular section
   of your recipe.

Remember, these are only guidelines and not requirements for you to submit a recipe.
If in doubt, send us a pull request and we will happily provide feedback.


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

Another very useful way to contribute to COSIMA Recipes is to review `existing
Pull Requests`_. Even if you don't have a new workflow to propose to the world,
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

Some tips for reviewing
^^^^^^^^^^^^^^^^^^^^^^^

* Does the PR have a concise description of the proposed changes? If not, request it.
* Have a look at the proposed changes. Do they make sense?
* Is the proposed code clean and clear?
* Are the proposed changes documented or commented? Methods should come with docstrings. But also documentation in the form of Markdown surrounding code is very appreciated. Code should be as generalisable as possible. We prefer documentation and code with variables and method names that are verbose and read like English. For example, the code below:


.. code-block:: python

    def znl_mean(ar):
        return ar.mean('xt_ocean')

has a few issues. First, the names don't read English. The method does not have any documentation nor is self-explanatory. Further, the method assumes that ``xt_ocean`` is a coordinate of the data array.

A much better version, free from all the cons mentioned above, is:

.. code-block:: python

    def zonal_mean(dataarray):
        '''
        Returns the (numerical) zonal mean of `dataarray`, i.e., its mean along latitude circles.

            Parameters:
                    dataarray (xarray.dataarray): An xarray dataarray

            Returns:
                    xarray.dataarray: The (numerical) zonal mean of `dataarray`
        '''

        return dataarray.cf.mean('longitude')
     

* Ensure that the notebook runs! To do that:

  - Clone the repository or the fork that the PR was made from;
  - Checkout the appropriate branch;
  - Ensure that the notebook runs when a **new** kernel is launched. Ensure that all cells run in sequential order, and that all cell outputs are evaluated.

.. _existing Pull Requests: https://github.com/COSIMA/cosima-recipes/pulls
