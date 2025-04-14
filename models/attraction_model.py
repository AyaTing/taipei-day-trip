def get_attraction_by_id(attraction_id, db):
    try:
        cursor = db.cursor(dictionary=True)
        select_query = "SELECT `a`.`id`, `a`.`name`, `a`.`category`, `a`.`description`, `a`.`address`, `a`.`transport`, `a`.`mrt`, `a`.`lat`, `a`.`lng`, GROUP_CONCAT(`image_url` SEPARATOR ', ') AS `images` FROM `attractions` `a` LEFT JOIN `attraction_images` `ai` ON `a`.`id` = `ai`.`attraction_id` WHERE `a`.`id` = %s GROUP BY `a`.`id`"
        cursor.execute(select_query, (attraction_id,))
        return cursor.fetchone()
    finally:
        cursor.close()

def get_mrts_data(db):
    try:
        cursor = db.cursor()
        select_query = "SELECT `mrt`, COUNT(*) AS `attraction_count` FROM `attractions` WHERE `mrt` IS NOT NULL GROUP BY `mrt` ORDER BY `attraction_count` DESC"
        cursor.execute(select_query)
        return cursor.fetchall()
    finally:
        cursor.close()