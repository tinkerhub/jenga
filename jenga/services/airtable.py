from airtable import Airtable


class AirTableDB:
    """
    Airtable class for all airtable opeartions to table
    """

    def __init__(self, base_key, api_key):
        self.member_table = Airtable(base_key, "Members", api_key)
        self.college_table = Airtable(base_key, "Campus", api_key)
        self.skill_set = Airtable(base_key, "Skills View List", api_key)

    def insert_member_details(self, data):
        return self.member_table.insert(data)

    def get_colleges(self):
        raw_college_list = self.college_table.get_all()
        college_list = [
            {
                "id": college.get("id"),
                "name": college.get("fields").get("Your campus/ school name"),
            }
            for college in raw_college_list
        ]
        return college_list

    def get_skills(self):
        raw_skills_list = self.skill_set.get_all()
        skills_list = [
            {
                "id": skill.get("id"),
                "name": skill.get("fields").get("Skill"),
            }
            for skill in raw_skills_list
        ]
        return skills_list

    def check_member_exist(self, member):
        member = self.member_table.search("MobileNumber", member)
        if len(member) != 0:
            return member[0]["id"]
        else:
            return False
