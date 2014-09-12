# Seed Drill

A seed drill is a sowing device that precisely positions seeds in the soil and then covers them. And this is a script to automate logging your times in [Harvest](http://getharvest.com) from [Taskwarrior](http://taskwarrior.org) tasks.

## Usage

`task harvest 3` - takes the time stored in task 3, and logs it in the appropriate project in Harvest, with the task type you specify.

Use `task start` and `task stop` as usual to track your time. When you're ready to log your time, type `task {id/uuid} mod actual:{time}` where `{time}` is the actual amount of time you spent on the task (maybe your Taskwarrior timer wasn't totally accurate). Then type `task harvest {id/uuid}` and you're done.

## Install

Clone this repo somewhere.

## Configuration

Quite a bit of configuration is needed. But don't worry, you only need to do this once.

### Taskwarrior Configuration

#### UDAs

Create the following UDAs in your `~/.taskrc` file.

```
uda.actual.type=duration
uda.actual.label=Actual Time

uda.harvestcomment.type=string
uda.harvestcomment.label=Harvest Comment

uda.harvestproject.type=numeric
uda.harvestproject.label=Harvest Project

uda.harvesttasktype.type=numeric
uda.harvesttasktype.label=Harvest Task Type
```

#### Add a command alias

Add something like the following to your `~/.taskrc`:

    $ alias.harvest=execute python /path/to/seed-drill/seed-drill/command.py

In this example, `harvest` is the name of the command (e.g. `task harvest 3`) but you can call this whatever you want.

### Seed Drill Configuration

#### Setup your credentials file

Create a file at `~/.harvest.credentials.json`. Enter this text, and update the subdomain, email and password values:

```
{
    "email": "{email}",
    "password": "{password}",
    "subdomain": "{subdomain}"
} 
```

#### Defining your task types

Replace `{subdomain}`, `{email}`, and `{password}` below:

    $ curl https://{subdomain}.harvestapp.com/daily -H 'Accept: application/json' -H 'Content-Type: application/json' -u {email}:{password} -X GET > ~/.harvest.tasks.json

Whenever you update your projects/task types in Harvest, you should re-run this command to get the latest data.

#### Create your project map

In Taskwarrior, you probably track projects with project names like `example` and `misc` or hopefully something more interesting than that. You need to define a mapping of Taskwarrior project names to Harvest project IDs. For example:

```
{
    "example": {
        "name": "Example project",
        "id": "5990760"
    },
    "misc": {
        "name": "Miscellany",
        "id": "6300599"
    }
}
```

Save this content in `~/.harvest.projects.json`. Look in the previously created `~/.harvest.tasks.json` to find project IDs.
