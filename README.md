Mathjobs-automator
==================

Tools for automating the process of applying for jobs on mathjobs.org

Instructions
---------------

1. Update template.tex to include your information.

2. Create a .csv file in the appropriate format (You can have a header row as long as the first column of the header row is "University"):
  - Name of University (e.g. University of California, Los Angeles)
  - Informal Name or blank (e.g. UCLA): note that the code generates this for common formats like University of BLAH
  - Job title(s): comma separated list of titles, or blank if you want to apply to any available position (e.g. Assistant Adjunct Professor, Research Postdoc)
  - Positions with a different mathjob id at the same institution that you are also applying for (e.g. Assistant Adjunct Professor in the Program in Computing)
  - Mathjobs url (e.g. https://www.mathjobs.org/jobs/jobs/2201): note that the code assumes that the id is 4 digits long.
  - Whether this position needs a Cover Letter: Y or blank
  - Whether this position needs a CV: Y or blank
  - Whether this position needs a Research Statement: Y or blank
  - Whether this position needs a Publication List: Y or blank
  - Custom message for school: Inserted into the cover letter.  If this column is blank, then a custom message is generated from data in the following columns
  - Prof1: The last name of a professor you would be interested in working with; a comma separated list of professors is also accepted
  - Code1: Either blank, "a", "f" or "fa."  An "f" indicates a female professor and an "a" indicates that you think the professors work is closely aligned with your interests (see the code for how this distinction affects the generated cover letter)
  - Topic1: A topic that the professor works on, e.g. "the $p$-adic Langlands correspondence," "representations of exceptional $p$-adic algebraic groups," or "Iwasawa theory"
  - Prof2: ...
  - Code2: ...
  - Topic2: ...
  - Prof3: ...
  - Code3: ...
  - Topic3: ... (you can actually have as many of these triples of columns as you'd like)
  - Due Date: This isn't actually used by the code, but the code does assume that there is an extra column with something in it.

Run generate_cover_letters (dry run with upload=False, then once you're happy with upload=True)

Run apply_for_jobs

Warnings
-------------

There may still be bugs in this code; in particular, it may make assumptions about the structure of the mathjobs website that are no longer accurate.  Use at your own risk.

Please remember to update the template before you use it.

If you use the apply_for_jobs function to automate your applications, note that the code currently does not handle follow-up pages.  Sometimes after you submit an application the school will request additional information from you.  For example they might ask whether you know any faculty at the school.  These questions are not currently answered by the script.  Rather, it will report that additional questions were asked and you need to go back and update the application.

Overuse
-----------

As a job applicant, I'm really happy with how mathjobs makes it easy to find and apply for jobs in math.  We have it a lot better than most other disciplines.  I worry that automating the process will encourage applicants to apply for even more positions.  Getting 1000+ applicants places a big burden on the professors making the decision on who to hire.  In consideration, please be thoughtful about which positions you actually need to apply to.