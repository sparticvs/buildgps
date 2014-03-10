# Data Specification

**Author:** sparticvs
**License:** Public Domain

## Summary

The purpose of this specification is to standardize output from the WebSockets
daemon to be consumed by a Javascript application that is displaying Build
information. The purpose of this specification is to be as general as possible
so that it can be build system agnostic (as well as repository and testing sytem)

## Data Formatting

All data sent from the server to the client will be in JSON format.  The purpose
of this is due to the fact that the intended consumer of the information is javascript
in a webpage.  Also JSON is easy to read as a human, so best of both worlds.

### Time Format

Time is to be transmitted in the ISO 8601 standard format.

### Message Format

Immediately after connecting to the WebSocket Daemon for a build system, the system
should immediately report the following packet:

    {
        "project": [
            {
                "name": "foobar",
                "build": {
                    "status": "success",
                    "timestamp": "2014-03-10T19:45:46+0000",
                    "label": "#4123",
                },
                "repo": {
                    "branch": "master",
                    "commit": "abcdef0123456789",
                    "blame": "sparticvs",
                    "timestamp": "2014-03-10T19:44:46+0000",
                }
            },
            {
                "name": "barbaz",
                "build": {
                    "status": "failure",
                    "timestamp": "2014-03-10T19:45:46+0000",
                    "label": "#1241",
                },
                "repo": {
                    "branch": "experimental",
                    "commit": "abcdef0123456789",
                    "blame": "sparticvs",
                    "timestamp": "2014-03-10T19:44:46+0000",
                }
            }
        ]
    }

#### Structure

    `project` - Contains an Array of Project Objects
    `project.name` - Project Name as reported by the Build System
    `project.build` - Object containing more information from the build system
    `project.build.status` - Current Build Status (Succes, Building, Failure)
    `project.build.timestamp` - Last Build Timestamp
    `project.build.label` - Label for the Build (Jenkins for instance does #<build number>)
    `project.repo` - Object containing repository information
    `project.repo.branch` - Name of the Branch that was built
    `project.repo.commit` - Commit Identifier (should be a string)
    `project.repo.blame` - Who get's the blame (or praise) for this commit
    `project.repo.timestamp` - Time when the commit was made
