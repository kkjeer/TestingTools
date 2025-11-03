/*
A KBase module: TestingTools
This sample module contains one small method that filters contigs.
*/

module TestingTools {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_TestingTools(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef run_FBAExplorer(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
