This folder contains the script used by the accessdev jenkins server to run all the notebooks weekly and confirm they are still in a working state.

For cells in notebooks which are expected to fail, you need to add a 'skip-execution' tag which will cause the cell to be skipped in automated testing. To do this, select the cell and open the Property Inspector (click on the icon with two cogged wheels on the right of JupyterLab) and add a tag with the text 'skip-execution'.