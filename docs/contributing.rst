Contributing to the Cookbook
============================

There are two main types of recipes that the Cookbook includes and we welcome contributions
to any of them:

Tutorials
   *Tutorials* are the most comprehensive kind of recipe. We intend for these
   to be an introduction to the tools we use, e.g., the Intake Catalog, and how to
   work with it, or the cartopy package. The tutorials should steer away from documenting
   any scientific analysis.

Recipes
   For demonstrating scientific uses of the Cookbook, one of your options
   is to create a *recipe*. These should be high-quality, well-documented workflow
   examples. Ideally, these showcase best-practice uses of the libraries such as `xarray`_,
   `cf-xarray`_, `pint`_, etc.

.. _xarray: https://xarray.dev/
.. _cf-xarray: https://cf-xarray.readthedocs.io/en/latest/
.. _pint: https://pint.readthedocs.io/en/stable/


Getting started with git
------------------------

Development of the Cookbook of Recipes is done in through `GitHub`_, so you'll
need to know how to work with the distributed version control software git to
be able to contribute back. A good set of resources for getting started with
git and GitHub is available on the `ACCESS-NRI Training`_ portal.

.. _GitHub: https://github.com/COSIMA/cosima-recipes
.. _ACCESS-NRI Training: https://access-nri.github.io/Training/HowTos/GitAndGitHub/


Working on your recipe
----------------------

In most cases, you'll want to be working on your recipes directly on HPC
infrastructure, such as `NCI`_. In this case, you should be familiar with
`running a Cookbook recipe at NCI`_, and particularly with running `on the ARE`_.
These guides will take you through cloning the Cookbook repository (which is,
a bit confusingly, called `cosima-recipes`_) and working with notebooks to
perform your analysis. Make use of git by *branching* and *committing*
(as described on the `GitHub git cheat sheet`_, for example).
You can interact with git through a terminal on your ARE session, or through
a direct connection to Gadi.

When you have developed your notebook to the point where you'd like to
contribute it to the main COSIMA Recipes repository, continue to the next
section. If you can't quite fully complete your notebook, you can seek advice
on the `ACCESS-Hive Forum`_, or submit it as a pull request anyway, asking for
feedback! Sometimes having more eyes on a problem can be useful, and other
people might not have to duplicate the full process if they can use your
notebook as a base.

.. _NCI: https://nci.org.au/
.. _cosima-recipes: https://github.com/COSIMA/cosima-recipes
.. _running a Cookbook recipe at NCI: https://github.com/COSIMA/cosima-cookbook/wiki/Beginners-Guide-to-the-COSIMA-Cookbook#running-cosima-recipes-at-nci
.. _on the ARE: https://github.com/COSIMA/cosima-cookbook/wiki/How-to-use-COSIMA-Cookbook-on-the-ARE-@-NCI
.. _GitHub git cheat sheet: https://training.github.com/downloads/github-git-cheat-sheet/
.. _ACCESS-Hive Forum: https://forum.access-hive.org.au/


Tips for making a good recipe
-----------------------------

As researchers, we often develop code as part of our research and most of
the time the main aim of code development is to find answers to questions
that have not yet been explored. Reproducibility may not always be considered
as part of the code development process or be a priority. If this is something
that resonates with you, or if you would like to learn more about making your
code shareable and reproducible, we are including some tips and good practices
to help you achieve this. 

1. Give the recipe a descriptive but generic title. Avoid being too specific
   as this will make it harder for other users to find code that matches their
   needs. For example, ``Computing pairwise distances between grid cells`` may be
   a better title than ``Computing distance between grid cells in the Southern
   Ocean and ice edge`` because the latter gives users the impression that
   the recipe is only relevant if they are looking at sea ice.

2. Include a short introduction summarising what your recipe is expected to
   do. You can include some information of the inputs needed to run your script,
   the expected outputs, and the methods you are using to get there. As with
   the title, we also recommend that you keep your description as generic as
   possible.

3. Give your variables and functions a descriptive name, so it is easy for
   users to read and follow your code. For example, ``mean_monthly_temperature_australia``
   is better than ``temp``. Of course, if you overdo it with being verbose
   it could be cumbersome, e.g., ``mean_monthly_temperature_over_east_australia_for_the_year_that_bushfires_were_a_big_issue``.

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
local clone of the repository. You'll need to then synchronise these changes
to GitHub to be able to propose them in a pull request. If you haven't already,
`create a fork`_ of the repository. Once you have pushed your
new branch onto your fork, you'll be able to `create a pull request`_.

.. _create a fork: https://docs.github.com/en/get-started/quickstart/fork-a-repo
.. _create a pull request: https://docs.github.com/en/get-started/quickstart/github-flow#create-a-pull-request


Reviewing existing Pull Requests
--------------------------------

Another very useful way to contribute to the Cookbook of Recipes is to review `existing
pull requests`_. Even if you don't have a new workflow to propose to the world,
you might be an expert in some part of the process and your feedback is valuable!

**Everyone can review and comment on pull requests.**

Take a look at the `existing pull requests`_ to see if anything takes your fancy.
There are two ways to interact with these, depending on what sort of feedback
you'd like to provide.

The simplest way to examine a pull request is to `use GitHub <https://github.com/COSIMA/cosima-recipes/pulls>`_. You can look at changes made to files
(GitHub will show you a standard linux ``diff`` for each file changed), read though commit messages, and/or peruse any comments
the community has made regarding this pull request.

Awkwardly, notebooks contain a lot of extra
metadata and structure, so it's not very pleasant to review them through a file diff!

Instead, the *review-notebook-app* bot will leave a comment with a **ReviewNB**
button on every pull request: this lets you leave your feedback on a representation
of the notebook itself.

Some tips for reviewing
^^^^^^^^^^^^^^^^^^^^^^^

* Does the pull request have a concise description of the proposed changes? If not, request it.
* Have a look at the proposed changes. Do they make sense?
* Is the proposed code clean and clear?
* Are the proposed changes documented or commented? Methods should come with docstrings. But also documentation in the form of Markdown surrounding code is very appreciated. Code should be as generalisable as possible. We prefer documentation and code with variables and method names that are verbose and read like English. For example, the code below:


.. code-block:: python

    def znl_mean(ar):
        return ar.mean('xt_ocean')

has a few issues. First, the names aren't easily understood. The method does not have any documentation, nor is it self-explanatory. Furthermore, the method assumes that ``xt_ocean`` is a coordinate of the data array; hard coding dimension names is fragile to future changes.

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

  - Clone the repository or the fork that the pull request was made from;
  - Checkout the appropriate branch;
  - Ensure that the notebook runs when a **new** kernel is launched. Ensure that all cells run in sequential order, and that all cell outputs are evaluated.

.. _existing Pull Requests: https://github.com/COSIMA/cosima-recipes/pulls

Do you need more help with the steps above? Read below:

To clone a pull request locally
+++++++++++++++++++++++++++++++

If you want to test pull requests locally (i.e., to compile or run the code),
you need to download the pull request branch. You can do this either by cloning the branch from the pull request.

In this context "locally" means somewhere you can run the code -- this is probably on Gadi, but may also be on a local machine.

If you are using ssh keys for command line authentication:

::

    git clone -b «THEIR_DEVELOPMENT_BRANCHNAME» git@github.com:«THEIR_GITHUB_USERNAME»/cosima-recipes.git

where «THEIR_GITHUB_USERNAME» is replaced by the username of the person proposing the pull request,
and «THEIR_DEVELOPMENT_BRANCHNAME» is the branch from their pull request.

Alternatively, you can add the repository of the user proposing the pull request as a remote to
your existing local repository. Navigate to your local repository and type

::

    git remote add «THEIR_GITHUB_USERNAME» git@github.com:«THEIR_GITHUB_USERNAME»/cosima-recipes.git

where «THEIR_GITHUB_USERNAME» is replaced by the user name of the person who has made the
pull request. Then download their pull request changes

::

    git fetch «THEIR_GITHUB_USERNAME»

and switch to the desired branch

::

    git checkout --track «THEIR_GITHUB_USERNAME»/«THEIR_DEVELOPMENT_BRANCHNAME»

You now have a local copy of the code from the pull request and can run tests locally.
If you have write access to the main repository you can push fixes or changes directly
to the pull request.
