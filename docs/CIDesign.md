Continuous Integration
======================

The process

1) Commit to repo
2) Notify CI that commit was made
3) Pull Code
4) Build in all supported scenarios
5) Run all unit-tests

Operation
------------
Shows all supported providers even if they need to be downloaded. If its needed
once, its needed again. This will need a key-chain of some type to manage
credentials.

Project Details
----------------

GET /projects

projects : [
    {
        name : "buildgps",
        description : "Continuous Integration with Direction",
        scm : {
            provider : "git",
            remote : "https://github.com/sparticvs/buildgps.git"
        },
        build_sys : {
            provider : "gnu-autotools" // Can be ANT, mvn, or some other system
        },
        unit_test : {
            provider : "check" // jUNIT, etc
        },
        branches : [
            {
                name : "master",
                environments : [
                    {
                        os : "Windows 7 (MinGW)",
                        cpu : "x86-64",
                        last_build : 1,
                    },
                    {
                        os : "Linux",
                        cpu : "armv7",
                        last_build : 2,
                    }
                ]
            }
        ],
        tags : []
    }
]


Build Details
--------------

GET /projects/buildgps/builds

builds : [
    {
        id : 1,
        trigger : "Commit abcdef1234567890 pushed to blessed repository",
        state : "complete",
        status : "failed,
        commit : "abcdef1234567890",
        blame : "sparticvs",
        start : 1234567890,
        end : 1234567899,
    }
]
