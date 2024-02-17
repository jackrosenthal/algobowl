# AlgoBOWL: Full Rules and Grading Info

AlgoBOWL is a group project for Algorithms courses.  Students
participate in teams of two to four to create a heuristic for an NP
hard problem, and put their algorithm up against the other teams in
the course.

A simplified explanation of the project can be found on the [AlgoBOWL
website](https://mines.algobowl.org).  This document constitutes a
complete set of rules for those interested.

## Competition Flow

The competition consists of 6 stages:

* Input Upload
* Output Upload
* Verification
* Resolution
* Open Verification
* Evaluation

Only one stage of the competition is active at a time (with the
exception of Open Verification and Evaluation, which are typically
scheduled concurrently).  Teams may only participate in currently
active stages (for example, a team is not permitted to upload an input
after Output Upload has begun).

Given the whole-class nature of the project, it's not possible for the
instructor to give individual extensions on any deliverable of the
project, as they'd need to give the extension for the entire class.
Students with approved absences during the project should ask the
instructor for an alternative activity.

## Problem Description

After forming teams, the instructor will distribute the problem
description.  This describes an NP-hard problem.  The description will
specify the input and output format you're expected to handle.  Your
team is expected to develop two computer programs:

* A program which takes an input and creates the best possible output
  you can.
* A program which takes an input and an output, and verifies if the
  output is valid according to the description in the problem
  statement.

The problem you're given is NP-hard, in that, it's unreasonable to
expect you can write a program which produces the _optimal_ answer for
inputs. Instead, we expect you to produce _valid_ outputs which are
the best you can compute in the time you're given.  It's important to
note that while a particular input may only have one _optimal_ output,
it likely has a very large number of _valid_ outputs.  When you're
writing your verifier program, you should verify the output is
_valid_, not that it's _optimal_.

In general, you may use any programming language you wish, as well as
any libraries/frameworks you wish, so as long as your team is the
author of the actual innovative algorithm which solves the problem
we've tasked you with.  For example, if we give you a graph problem,
you're welcome to use any graph libraries that are available for your
programming language, but if that library includes an algorithm which
implements a heuristic for any NP-hard problem, you should refrain
from using those functions.

Aside from language and library documentation, you should not
reference the internet while creating your solution.  For example,
going and reading research papers on any NP-hard problem is strictly
prohibited.

Your instructor may request code submission to uphold your team's
integrity.  Additionally, the winning teams are often asked to present
their solutions to the class.

## Input Upload

Your team should create an input according to the problem statement.
Upload your input to the AlgoBOWL website before the deadline.  You
can upload multiple times, and only the latest upload will be used.

You should write your input in a plain text ("ASCII") formatted file.
The site is tolerant of both UNIX and MS-DOS style line endings, but
it's recommended to use UNIX style line endings.  If you're authoring
the input by hand, you should use a plain-text editor (such as Vim,
Notepad, Emacs, Vscode, etc.), not a rich text editor (such as Word).

The AlgoBOWL site will verify your input meets the requirements from
the problem statement, and notify you if changes are required.  The
site will re-format your input for consistency before it's distributed
to other groups (for example, we'll ensure consistent spacing and
UNIX-style newlines).

### Grading

* 5 points for uploading any valid input.
* 10 points will be awarded based on how "difficult" your input was.
  Difficulty is defined by the number of groups which find the best
  solution.  You will be awarded 10 points if only one group finds
  the best solution, and we subtract 1 point for each additional group
  which finds the best solution.  For example, if 4 groups all get a
  rank of 1 on your input, you will be awarded `10-(4-1) = 7` points.
  If 11 or more groups get a rank of 1, you'll be awarded no points in
  this category.  When designing your input, keep this in mind.  Try
  to design an input you think will be very hard to find the optimal
  solution.

### Default

Should your team fail to upload an input before the deadline, you'll
get no points for input upload.  Your team will receive an
automatically-generated random input which you'll be able to use later
for the Verification stage.


### Team Name

During input upload, you'll also be asked to create a team name.  This
name will be shown on the leaderboards!  You are encouraged to be
creative, but avoid names which could be considered offensive.  Your
instructor reserves the right to change your team name at their own
discretion.


## Output Upload

During output upload, you'll receive all input files from all teams,
and you'll need to generate outputs for each input.  Upload all
outputs before the deadline.

Similar to Input Upload, all outputs you upload will automatically be
re-formatted for consistency.  The site may check for basic formatting
errors during upload, however, it will not ensure your output is
actually valid.  It is highly recommended to run your verifier program
on all outputs before you actually upload them.  Additionally, please
be very careful to only upload the correct output for each input.
Including the group number in each output filename is an easy way to
double-check as you're uploading.

You can upload outputs as many times as you like during Output Upload,
but only your latest output uploaded for each input will be used.

Preliminary rankings will start to become visible on the leaderboard,
but please be aware that nothing is verified yet, and they often
change after verification.

### Compute Resources

You are generally allowed to use any compute resources available to
you to run your solver, but we ask that you do not heavily abuse
shared resources provided by the school (e.g., Isengard server or lab
computers), as other students may need these resources for other
classes or projects.  It's OK to run your solver on a few school lab
computers, but please do not massively-distribute your computation
across many lab computers.

### Grading

* 50 points will be given based on the percentage of inputs that you
  upload a valid output for.  Validity will be determined with the
  instructor's verifier, not other groups.  For example, if there's 10
  groups in the competition, and you uploaded 9 valid outputs, you'd
  receive `(9/10)*50` = 45 points in this category.
* 15 points will be awarded based on how "good" your outputs are.  We
  do this by creating two benchmark solutions.  If you're below
  Benchmark 1 (the easier benchmark), you'll receive between 0 and 5
  points (based on your relative standings compared to all other
  groups below Benchmark 1).  If you're above Benchmark 1, but below
  Benchmark 2, you'll receive between 5 and 10 points.  Finally, if
  you're above both benchmarks, you'll receive between 10 and 15
  points.  Only the winning team will receive a full 15 points in this
  category.

### Default

If your team fails to upload all outputs during this time, you'll get
a second chance during the Resolution stage.  Outputs uploaded during
Resolution will still count towards your grade for this stage.

## Verification

During this stage, your team will be able to download all outputs
uploaded for your input.  Run your verifier program and mark each
output as either valid or invalid.  You can refer to the problem
statement for a definition of validity.

### Grading

* 20 points will be given based on your accuracy.  For example, if
  there's 10 teams in the competition, and you mark 8 verifications
  correctly, 1 falsely as invalid (when it was supposed to be valid),
  and 1 falsely as valid (when it was supposed to be invalid), your
  score in this category will be `(8/10)*20` = 16 points.

### Default

Outputs you do not verify will count against your accuracy.  For
example, if there's 10 teams in the competition, and you only verify 5
teams (but do all 5 accurately), you'll receive only 10 points in this
category.

The instructor's verification will be used in the case that you do not
verify.


## Resolution

The resolution stage is an _optional_ stage.  If you had outputs which
were rejected, you will have the opportunity to either:

* Upload a new output.  The instructor's verification will be used,
  and you'll get instant feedback if it's valid.  However, you may
  only upload once.  Once you upload during resolution, your output
  will be finalized and cannot be replaced again.
* Protest the verification.  The instructor's verification will be
  used.  You will have no chance to re-upload after protesting and
  your output will be finalized.

Additionally, you can use this chance to upload outputs you never
submitted during Output Upload.  But please keep in mind that you only
get once chance to upload each output, as the instructor's
verification will be applied immediately.

Finally, if there's any outputs you uploaded that were accepted, but
you know should've been rejected, you do have the chance to re-upload
new outputs.  Similarly, you only have a single chance to upload each
output.  You may want to do this, as if your output gets discovered
during Open Verification, you'll have no chance to correct it.

Please note that all outputs uploaded during Resolution will give a
penalty on the leaderboard.  This helps keep the competition fair for
those who uploaded everything during Output Upload.  Penalties on the
leaderboard have no effect on your grade.

### Grading

There are no points allocated specifically to this stage, as it's
optional.  However, participating in it can improve your grade for the
Output Upload stage, so it's recommended for everyone who got outputs
rejected.

## Default

If you don't participate in this stage, your outputs will remain unchanged.

## Open Verification

Open Verification is an _optional_ stage.  Participation is only
required if you wish to help improve the overall verification accuracy
of the competition.

During this stage, you have access to all inputs and all outputs, and
can protest any verification you believe to be incorrect.  With each
protest, please include a brief reason you believe the verification to
be incorrect.

* If your protest is correct, the verification will be updated immediately.
* If your protest is invalid (the original verification was correct),
  your team will receive a penalty on the leaderboard.

### Grading

This stage does not affect your grade.

## Evaluation

Evaluation is the stage where you share feedback on your teammates'
contributions to the project.  You'll submit the relative amount of
work in percentages each member contributed.

Ideally, we hope everyone contributed equally, but we recognize that
in any group project, not everyone pulls the same weight.

All forms of contributions should be considered holistically in this
assessment.  Please consider:

* Contribution to the algorithm design
* Contribution to coding the algorithm
* Debugging and assistance
* Writing the verifier program
* Running and monitoring programs
* Additional tooling and scripts developed
* Team administration (e.g., coordinating schedules, getting people
  together, ordering pizza, etc.)

Please note your instructor may require you to submit additional info
beyond the AlgoBOWL site.

### Grading

Your grade may be scaled (up or down) at the instructor's discretion
from your team's grade.

### Default

If you do not submit evaluations, we assume you mean that everyone
contributed equally on your team.
