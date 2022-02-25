

class File:
    def __init__(self, contributors:list, projects:list):
        self.contributors = contributors
        self.projects = projects


class Contributor:
    def __init__(self, name:str, skills: list):
        self.name = name
        self.skills = skills
        self.next_available = 0

    def __eq__(self, other):
        return self.name == other.name
        
    def __hash__(self):
        return hash(self.name)

    def has_skill(self, skill, mentoring:bool) -> (bool, int):
        """
            Check whether the specified contributor has this skill, taking into account whether or not there is mentoring.
        """
        
        # check if any of the skills we have conforms to this
        for our_skill in self.skills:
            if our_skill.name != skill.name:
                continue
            
            # our skill must be higher or equal than the specified skill
            if our_skill.level >= skill.level:
                return True, our_skill
            # unless we have mentoring
            elif mentoring and our_skill.level >= (skill.level-1):
                return True, our_skill

        return False, None

    def can_join_project(self, project, mentoring:bool):
        """
            Check whether this contributor can join the specified project, taking into account whether or not there is mentoring.
        """
        # go over the skills in the project
        for proj_skill in project.skills:
            if self.has_skill(skill=proj_skill, mentoring=mentoring)[0]:
                return True

        return False


class Skill:
    def __init__(self, name:str, level:int):
        self.name = name
        self.level = level
        self.contributor = None

    def has_contributor(self):
        return self.contributor is not None

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

class Project:
    def __init__(self, name:str, days:int, score:int, deadline:int, skills:list):
        self.name = name
        self.days = days
        self.score = score
        self.deadline = deadline
        self.skills = skills

def parse_file(filename:str) -> File:
    """
        Read the specified file and parse into a File object.
    """

    with open(filename, "r") as f:
        first_line = f.readline().split(" ")
        nr_contributors = int(first_line[0])
        nr_projects = int(first_line[1])

        file = File([], [])

        for contributor in range(nr_contributors):
            c_line = f.readline().split(" ")
            new_contributor = Contributor(c_line[0], [])

            for skill in range(int(c_line[1])):
                s_line = f.readline().split(" ")
                new_skill = Skill(s_line[0], int(s_line[1]))
                new_contributor.skills.append(new_skill)

            file.contributors.append(new_contributor)
            
        for project in range(nr_projects):
            p_line = f.readline().split(" ")
            new_project = Project(p_line[0], int(p_line[1]), int(p_line[2]), int(p_line[3]), [])
            
            for role in range(int(p_line[4])):
                s_line = f.readline().split(" ")
                new_skill = Skill(s_line[0], int(s_line[1]))
                new_project.skills.append(new_skill)

            file.projects.append(new_project)

        return file


class OutProject:
    def __init__(self, name : str):
        self.name = name
        self.contributors = ""
    
    def add_contributor(self, contributor : str):
        if self.contributors == "":
            self.contributors = contributor
        else:
            self.contributors += f" {contributor}"




def output_file(projects:list, filename:str):
    with open(filename, 'w') as file:
        file.write(str(len(projects)) + '\n')
        for project in projects:
            file.write(project.name + '\n')
            file.write(project.contributors + '\n')

def check_project(project, contributors, assigned_contributors_final):


    # keep track of the currently used contributors for this project
    assigned_contributors_temp = {}
    mentored_skills = set()

    outproject = OutProject(project.name)
    # check that all skills are covered
    for skill in project.skills:
        
        # go over the contributors
        for contributor in contributors:

            # already assigned to another skill
            if contributor in assigned_contributors_temp:
                continue # skip contributor

            mentoring_available = skill in mentored_skills

            has_skill, contr_skill = contributor.has_skill(skill, mentoring_available)

            if has_skill:
                # add to project
                skill.contributor = contributor
                assigned_contributors_temp[contributor] = skill
                outproject.add_contributor(contributor.name)
                if contr_skill.level >= skill.level:
                    mentored_skills.add(skill)
                break



        # check that the skill has been assigned
        if skill.contributor is None:
            return "Again", None, None
        

    available_times = [x.next_available for x in assigned_contributors_temp]
    possible_start = max(available_times)
    if possible_start >= project.deadline + project.score:
        return False, None, None

    for contributor in assigned_contributors_temp:
        contributor.next_available = possible_start + project.days
        # level up contributor
        project_skill = assigned_contributors_temp[contributor]

        mentoring_available = skill in mentored_skills

        contributor_skill = contributor.has_skill(project_skill, mentoring_available)[1]
        if contributor_skill.level <= project_skill.level:
            contributor_skill.level += 1

    return True, outproject, set()


def main(in_filename: str, out_filename:str):
    file = parse_file(in_filename)

    # sort by deadline
    file.projects = sorted(file.projects, key=lambda x: x.deadline)

    assigned_contributors = set()
    # maps contributors to projects
    
    # maps projects to contributors
    project_contributors = dict()

    # permanently assigned contributors
    assigned_contributors_final = set()

    appended = {}

    outprojects = []
    for project in file.projects:
        result, outproject, assigned_contributors_temp = check_project(project, file.contributors, assigned_contributors_final)

        if not result:
            continue # skip project

        if result == "Again":
            if project.name in appended:
                if appended[project.name] < 5:
                    appended[project.name] += 1
                    file.projects.append(project)
            else:
                file.projects.append(project)
                appended[project.name] = 0
            continue
            
        #print(f"Project '{project.name}' is approved.")

        # if we reach this, the project has been approved
        assigned_contributors_final = assigned_contributors_final.union(assigned_contributors_temp)

        if outproject.contributors != "":
            outprojects.append(outproject)

    output_file(projects=outprojects, filename=out_filename)



if __name__ == '__main__':
    main("input_data/a_an_example.in.txt", "output_a.txt")
    main("input_data/b_better_start_small.in.txt", "output_b.txt")
    main("input_data/c_collaboration.in.txt", "output_c.txt")
    main("input_data/d_dense_schedule.in.txt", "output_d.txt")
    main("input_data/e_exceptional_skills.in.txt", "output_e.txt")
    main("input_data/f_find_great_mentors.in.txt", "output_f.txt")

