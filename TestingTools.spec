/*
Tools for testing KBase apps: TestingTools
This module contains several methods that run various KBase apps and generate tests based on the results.
*/

module TestingTools {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        Each of these functions accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_TestingTools(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef run_FBAExplorer(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef run_TestFeedback(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef run_FBAExperiments(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef run_MetamorphicFeedback(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
