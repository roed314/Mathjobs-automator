#*****************************************************************************
#       Mathjobs - Automator
#
#       Copyright (C) 2012 David Roe <roed.math@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

import copy
import os
import mechanize
import csv
import re
from subprocess import call

# Faculty contacts in department

def skip(line):
    return line[0] == "University"

def school_name(line):
    return line[0]

def informal_school_name(line):
    if len(line[1]) > 0:
        return line[1]
    school_name = line[0]
    if school_name.startswith("University of") or school_name.endswith("Institute of Technology"):
        return "the " + school_name
    if school_name.endswith(" University"):
        return school_name[:-11]
    if school_name.endswith(" College"):
        return school_name[:-8]
    return school_name

def underscore_school_name(line):
    return line[0].replace(" ","_").replace("'","")

def app_number(line):
    return job_description_url(line).strip()[-4:]

def job_title(line):
    titles=line[2]
    if len(titles) == 0:
        final = "to any available postdoctoral positions available at %s"%(informal_school_name(line))
    elif titles.find(",") != -1 or titles.find(" and ") != -1:
        final = "for the positions of %s"%(titles)
    else:
        final = "for the position of %s"%(titles)
    others = line[3]
    if len(others) > 0:
        final += " (note that I am submitting a separate application for the position of %s; if it is convenient to only use one of these applications feel free to do so)"
    return final

def job_description_url(line):
    return line[4]

# should detect these from the url...
def needs(line, title):
    if title == "Cover Letter":
        return needs_cov(line)
    if title == "Curriculum Vitae":
        return needs_cv(line)
    if title == "Research Statement":
        return needs_rs(line)
    if title == "Teaching Statement":
        return needs_ts(line)
    if title == "Publication List":
        return needs_pl(line)
    raise ValueError, "Unknown submission type"

def num_needed(line):
    return int(needs_cov(line)) + int(needs_cv(line)) + int(needs_rs(line)) + int(needs_ts(line)) + int(needs_pl(line))

def needs_cov(line):
    return len(line[5]) > 0

def needs_cv(line):
    return len(line[6]) > 0

def needs_rs(line):
    return len(line[7]) > 0

def needs_ts(line):
    return len(line[8]) > 0

def needs_pl(line):
    return len(line[9]) > 0

def enclosed(line):
    L = []
    if needs_cv(line):
        L.append("Curriculum Vita")
    if needs_rs(line):
        L.append("Research Statement")
    if needs_ts(line):
        L.append("Teaching Statement")
    if needs_pl(line):
        L.append("Publication List")
    return " \\\\ ".join(L)

def school_specific(line):
    if len(line[10]) > 0:
        return line[10]
    profs = line[11:-1:3]
    alignments = line[12:-1:3]
    topics = line[13:-1:3]
    assert len(profs) == len(topics) == len(alignments)
    i = 0
    n_align = 0
    while i < len(profs):
        if len(profs[i]) == 0:
            profs.pop(i)
            topics.pop(i)
            alignments.pop(i)
        else:
            # We just use last names for now:
            while profs[i].find("  ") != -1:
                profs[i] = profs[i].replace("  ", " ")
            profs[i] = ", ".join([a.strip().split(" ")[1] if len(a.strip().split(" ")) > 1 else a for a in profs[i].split(",")])
            if alignments[i].find("a") != -1:
                if n_align > 0:
                    raise ValueError("For simplicity, we only allow one aligned professor group per line.  You can include more than one professor with the same topic though.  Just put them in the same column, separated by commas.")
                n_align += 1
                if i > 0:
                    profs.insert(0,profs.pop(i))
                    topics.insert(0,topics.pop(i))
                    alignments.insert(0,alignments.pop(i))
            i += 1
    if len(profs) == 0:
        return default_school_statement(line)
    genders = ["him" if a.lower().find("f") == -1 else "her" for a in alignments]
    L = []
    n_align = 0
    n_interest = 0
    for prof, topic, a, gender in zip(profs, topics, alignments, genders):
        if prof.find(",") != -1:
            many = True
            prof = [p.strip() for p in prof.split(",")]
        else:
            many = False
        if len(topic) == 0:
            # this case should only be used when you don't have much to say.
            # So we require that len(profs) == 1
            if len(profs) > 1:
                raise ValueError, "Either put all professors in one column, or specify topics of interest"
            return prof_research_sentence(line, prof, gender, many)
        elif a.find("a") != -1:
            L.append(aligned_research_sentence(prof, topic, gender, many))
            n_align += 1
        else:
            if many:
                raise NotImplementedError("Saying a list of professor's research on blah is interesting: lame")
            L.append(interesting_research_sentence(prof, topic, gender, n_interest, n_interest+n_align))
            n_interest += 1
    L.append(concluding_school_statement(line, n_align + n_interest))
    return "  ".join(L)
    
def aligned_research_sentence(prof, topic, gender, many):
    if many:
        return "The research of Professors %s on %s meshes very well with my research goals, and I'm excited by the opportunity to collaborate with them."%(", ".join(prof[:-1]) + " and " + prof_list[-1], topic)
    else:
        return "Professor %s's research on %s meshes very well with my research goals, and I'm excited by the opportunity to collaborate with %s."%(prof, topic, gender)

def interesting_research_sentence(prof, topic, gender, n_interest, n_total):
    if n_total > 2:
        raise NotImplementedError("Need more grammar cases")
    if n_interest == 0:
        return "Professor %s's research on %s %sintrigues me, and I would enjoy the opportunity to learn more and collaborate with %s."%(prof, topic, "also " if n_total > 0 else "", gender)
    if n_interest == 1:
        return "%sI %sfind Professor %s's work on %s interesting and hope to have occasion to speak to %s about it."%("Finally, " if n_total == 2 else "", "also " if n_total == 1 else "", prof, topic, gender)
    raise NotImplementedError("Need additional distinct sentences")

def prof_research_sentence(line, prof, gender, many):
    if many:
        return "I believe that my work may be of interest to Professors %s and that their presence will make %s an excellent place for me to continue my work and explore new collaborations."%(", ".join(prof[:-1]) + " and " + prof[-1], informal_school_name(line))
    else:
        return "I believe that my work may be of interest to Professor %s and that %s presence will make %s an excellent place for me to continue my work and explore new collaborations."%(prof, "his" if gender == "him" else "her", informal_school_name(line))

def default_school_statement(line):
    return "I believe that %s will provide an excellent venue to continue my work and explore new collaborations."%(informal_school_name(line))

def concluding_school_statement(line, n_total):
    if n_total == 0:
        raise RuntimeError
    if n_total == 1:
        return "As a consequence, I believe that %s would provide an excellent venue to pursue my postdoctoral studies."%(informal_school_name(line))
    else:
        return "The concentration of compatible faculty at %s suggests that it would provide an excellent environment to pursue my postdoctoral studies."%(informal_school_name(line))

templating_functions = {
"1":school_name,
"2":job_title,
"3":school_specific,
"4":enclosed}

def write_latex_file(filename, template, line):
    for n, func in templating_functions.iteritems():
        template = template.replace("#%s"%n,func(line))
    with open(filename, "w") as F:
        F.write(template)

def mathjobs_browser(email, password):
    print "Logging on to mathjobs..."
    br = mechanize.Browser()
    br.open("https://www.mathjobs.org/jobs?info-ja")
    br.select_form(name="ja")
    br["email"] = email
    br["pass"] = password
    br.submit()
    if not br.title().startswith("My Portfolio"):
        raise ValueError("Failed to log on to MathJobs.  Check your username and password.")
    return br

def generate_cover_letters(csv_filename, template_filename, cleanup=True, upload=False, email=None, password=None):
    csv_filename = os.path.abspath(csv_filename)
    orig_dir = os.getcwd()
    os.chdir(os.path.dirname(csv_filename))
    with open(template_filename) as template_file:
        template = template_file.read()
    if upload:
        br = mathjobs_browser(email, password)
        
    with open("/dev/null", "w") as devnull:
        with open(csv_filename, "rb") as csv_file:
            reader = csv.reader(csv_file)
            for line in reader:
                if skip(line):
                    continue
                print "Generating cover letter for %s"%(informal_school_name(line))
                write_latex_file("Cover_Letter_%s_%s.tex"%(app_number(line), underscore_school_name(line)), template, line)
                retcode = call(["pdflatex", "Cover_Letter_%s_%s.tex"%(app_number(line), underscore_school_name(line))], stdout=devnull)
                if cleanup:
                    retcode = call(["rm", "Cover_Letter_%s_%s.tex"%(app_number(line), underscore_school_name(line))])
                    retcode = call(["rm", "Cover_Letter_%s_%s.log"%(app_number(line), underscore_school_name(line))])
                    #retcode = call(["rm", "Cover_Letter_%s_%s.syctex.gz"%(app_number(line), underscore_school_name(line))])
                    retcode = call(["rm", "Cover_Letter_%s_%s.aux"%(app_number(line), underscore_school_name(line))])
                if upload:
                    print "Uploading cover letter for %s..."%(informal_school_name(line))
                    with open("Cover_Letter_%s_%s.pdf"%(app_number(line), underscore_school_name(line))) as spdf:
                        br.follow_link(text_regex="Cover Letter")
                        br.select_form(nr=0)
                        br.form.add_file(spdf, filename="Cover_Letter_%s_%s.pdf"%(app_number(line), underscore_school_name(line)))
                        br["Name"] = informal_school_name(line) + " (%s)"%(app_number(line))
                        br.submit()
                    if cleanup:
                        retcode = call(["rm", "Cover_Letter_%s_%s.pdf"%(app_number(line), underscore_school_name(line))])
    if upload:
       br.follow_link(text_regex="Logout") 
    os.chdir(orig_dir)

def find_select_name(app_part, resp, line):
    match = re.search('<b><b>' + app_part + r'</b></b></td><td style="white-space:nowrap"><select name="([^"]*)" >', resp.get_data())
    if match is None and needs(line, app_part):
        return match, "ERROR!  No place to input %s"%app_part
    if match is not None and not needs(line, app_part):
        return match, "ERROR!  %s required but not generated"%app_part
    return match, None

def apply_for_jobs(csv_filename, email, password, **kwds): #research_statement_name=None, teaching_statement_name=None, pub_list_name=None):
    """
    Valid keywords: "Research_Statement", "Teaching_Statement", "Publication_List"
    """
    csv_filename = os.path.abspath(csv_filename)
    orig_dir = os.getcwd()
    os.chdir(os.path.dirname(csv_filename))
    br = mathjobs_browser(email, password)
    error_list = []
    update_list = []
    submission_responses = []
    with open(csv_filename, "rb") as csv_file:
        reader = csv.reader(csv_file)
        for line in reader:
            if skip(line):
                continue
            print "Applying to %s..."%(informal_school_name(line))
            try:
                br.open(job_description_url(line))
            except mechanize.HTTPError:
                print "ERROR!  Job description URL failed to open"
                error_list.append(informal_school_name(line))                
                continue
            try:
                resp = br.follow_link(text_regex="Apply")
            except mechanize.LinkNotFoundError:
                print "ERROR!  Failed to follow application link"
                error_list.append(informal_school_name(line))                
                continue
            if re.search('<b>Additional questions for the AMS Cover Sheet</b>', resp.get_data()) is not None:
                print "Additional questions detected!  Please update your application at %s"%(br.geturl())
                update_list.append(informal_school_name(line))
            try:
                br.select_form(nr=0)
            except mechanize.FormNotFoundError:
                print "ERROR!  No Submission passible"
                error_list.append(informal_school_name(line))                
                continue
            if num_needed(line) != resp.get_data().count('</b></b></td><td style="white-space:nowrap"><select name='):
                print "ERROR!  Number of required items does not match"
                error_list.append(informal_school_name(line))                
                continue
            for app_name, app_value in (("Cover Letter", app_number(line) + "_" + underscore_school_name(line)[:22]),) + tuple(kwds.iteritems()):
                match, error = find_select_name(app_name.replace("_"," ").title(), resp, line)
                if error is not None:
                    print error
                    error_list.append(informal_school_name(line))
                    break
                if match is not None:
                    app_code = match.groups()[0]
                    app_control = br.form.find_control(name = app_code)
                    app_control.set_value_by_label([app_value])
            if error is not None:
                continue
            sr = br.submit()
            if re.search("<title>Thank you for your application</title>", sr.get_data()) is None:
                print "ERROR!  Submission %s failed"%(len(submission_responses))
                error_list.append(informal_school_name(line))
            submission_responses.append(sr)
    if len(error_list) > 0:
        print "Errors occurred in the applications to %s"%(', '.join(error_list))
    else:
        print "All submissions were successful"
    if len(update_list) > 0:
        print "Please answer the application questions for %s"%(', '.join(update_list))
    br.follow_link(text_regex="Logout")
    os.chdir(orig_dir)
    return submission_responses
