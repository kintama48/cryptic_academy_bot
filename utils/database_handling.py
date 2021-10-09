import psycopg2


class Database:
    def __init__(self):
        self.db = psycopg2.connect(host="ec2-52-86-123-180.compute-1.amazonaws.com", database="dat7agnicbs2gm",
                                   user="iwirbfnitvnsqc", port=5432,
                                   password="178c1ac45becf6badf4325b6f03c745863e5175494707405eaa43f8200d04292")

    def get_scholar_percentage(self, discord_id: int=None, ronin=None):
        if discord_id:
            cur = self.db.cursor()
            cur.execute('SELECT discord_id FROM ronin_discord_id;')
            list_of_discords = list()
            for i in cur.fetchall():
                list_of_discords.append(i[0])
            if discord_id in list_of_discords:
                cur.execute(f"SELECT percentage FROM ronin_discord_id WHERE discord_id={discord_id};")
                percentage = cur.fetchone()[0]
                return float(percentage)
            return None
        elif ronin:
            cur = self.db.cursor()
            cur.execute('SELECT ronin FROM ronin_discord_id;')
            list_of_ronins = list()
            for i in cur.fetchall():
                list_of_ronins.append(i[0])
            if ronin in list_of_ronins:
                cur.execute(f"SELECT percentage FROM ronin_discord_id WHERE ronin='{ronin}';")
                percentage = cur.fetchone()[0]
                return float(percentage)
            return None

    def set_scholar_percentage(self, discord_id: int, percentage: float):
        cur = self.db.cursor()
        cur.execute('SELECT discord_id FROM ronin_discord_id;')
        list_of_discord_ids = list()
        for i in cur.fetchall():
            list_of_discord_ids.append(i[0])
        if discord_id in list_of_discord_ids:
            cur.execute(f"UPDATE ronin_discord_id SET percentage={percentage} where discord_id={discord_id};")
            self.db.commit()
            cur.close()
            self.db.close()
            return "*Successfully updated your scholar percentage in the database!*"
        else:
            return "*You have not set your ronin:address yet. Please use the `<prefix>setronin` command first.*"

        # else:
        #     cur.execute(f"INSERT INTO ronin_discord_id (ronin, discord_id, percentage) VALUES ('{ronin_address}', {discord_id}, {percentage})")
        #     self.db.commit()
        #     cur.close()
        #     self.db.close()
        #     return "*Successfully added your scholar percentage to the database!*"

    def delete_percentage(self, discord_id: int):
        cur = self.db.cursor()
        cur.execute('SELECT discord_id FROM ronin_discord_id;')
        list_of_discord_ids = list()
        for i in cur.fetchall():
            list_of_discord_ids.append(i[0])
        if discord_id in list_of_discord_ids:
            cur.execute(
                f"UPDATE ronin_discord_id SET percentage=null WHERE discord_id={discord_id};")
            self.db.commit()
            cur.close()
            self.db.close()
            return "*Successfully deleted scholar percentage from the database!*"
        else:
            return "*You did not set your scholar percentage. Please use the `<prefix>share` command first!*"


    def get_scholar_by_ronin(self, ronin_address):
        ronin_address = ronin_address.replace('ronin:', '0x')
        cur = self.db.cursor()
        cur.execute('SELECT ronin FROM ronin_discord_id;')
        list_of_ronin = list()
        for i in cur.fetchall():
            list_of_ronin.append(i[0])
        if ronin_address in list_of_ronin:
            cur.execute(f"SELECT discord_id FROM ronin_discord_id WHERE ronin='{ronin_address}';")
            ronin_discords = list()
            for i in cur.fetchall():
                ronin_discords.append(i[0])
            return ronin_discords
        return None

    def get_ronin_by_id(self, discord_id: int):
        cur = self.db.cursor()
        cur.execute('SELECT discord_id FROM ronin_discord_id;')
        list_of_discord_ids = list()
        for i in cur.fetchall():
            list_of_discord_ids.append(i[0])
        if discord_id in list_of_discord_ids:
            cur.execute(f"SELECT ronin FROM ronin_discord_id WHERE discord_id={discord_id};")
            ronin = cur.fetchone()[0]
            return ronin
        return None

    def remove_ronin_db(self, discord_id: int):
        cur = self.db.cursor()
        cur.execute('SELECT discord_id FROM ronin_discord_id;')
        list_of_discord_ids = list()
        for i in cur.fetchall():
            list_of_discord_ids.append(i[0])
        if discord_id in list_of_discord_ids:
            cur.execute(
                f"DELETE FROM ronin_discord_id WHERE discord_id={discord_id};")
            self.db.commit()
            cur.close()
            self.db.close()
            return "*Successfully removed your ronin:address from the database!*"
        else:
            return "*Not found in the database!*"

    def set_ronin_db(self, ronin_address, discord_id):
        if not ronin_address:
            return "*Please provide a valid ronin:address!*"
        ronin_address = ronin_address.replace('ronin:', '0x')
        cur = self.db.cursor()
        cur.execute('SELECT discord_id FROM ronin_discord_id;')
        list_of_discord_id = list()
        for i in cur.fetchall():
            list_of_discord_id.append(i[0])
        if discord_id in list_of_discord_id:
            cur.execute(f"UPDATE ronin_discord_id SET ronin='{ronin_address}' where discord_id={discord_id};")
            self.db.commit()
            cur.close()
            self.db.close()
            return "*Successfully updated your ronin:address in the database!*"
        else:
            cur.execute(f"INSERT INTO ronin_discord_id (ronin, discord_id) VALUES ('{ronin_address}', {discord_id})")
            self.db.commit()
            cur.close()
            self.db.close()
            return "*Successfully added your ronin:address to the database!*"
