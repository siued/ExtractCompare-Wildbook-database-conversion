import json

import xlwt
from wildbook_util import get_aids, get_comments
from other_util import show_message, custom_sort


def export_to_excel(server_url):
    print('Starting export to excel')
    with open('sightings.json', 'r') as f:
        sightings = json.load(f)

    for sighting in sightings:
        sighting['image'] = 'no'

    aids = get_aids(server_url)

    notes = get_comments(aids, server_url)

    for note in notes:
        try:
            note_dict = json.loads(note)
        except json.decoder.JSONDecodeError:
            continue
        note_dict['image'] = 'yes'
        sightings.append(note_dict)

    # export to new Excel file

    sightings.sort(key=lambda x: custom_sort(x['id']))

    wb = xlwt.Workbook()
    sheet = wb.add_sheet('Sightings')
    sheet.write(0, 0, 'Name')
    sheet.write(0, 1, 'Old Name')
    sheet.write(0, 2, 'Date')
    sheet.write(0, 3, 'Age')
    sheet.write(0, 4, 'Gender')
    sheet.write(0, 5, 'Location')
    sheet.write(0, 6, 'With pup')
    sheet.write(0, 7, 'Image')
    sheet.write(0, 8, 'Comments')

    for i, sighting in enumerate(sightings):
        index = i + 1
        sheet.write(index, 0, sighting['id'])
        sheet.write(index, 1, sighting['orig_ID'])
        sheet.write(index, 2, sighting['date'])
        sheet.write(index, 3, sighting['age'])
        sheet.write(index, 4, sighting['gender'])
        sheet.write(index, 5, sighting['location'])
        sheet.write(index, 6, sighting['with_pup'])
        sheet.write(index, 7, sighting['image'])
        sheet.write(index, 8, sighting['comments'])

    # resize columns
    for i in range(8):
        sheet.col(i).width = 256 * 15
    sheet.col(8).width = 256 * 50

    try:
        wb.save('sightings.xls')
    except PermissionError:
        show_message('Error while saving', 'Please close the sightings.xls file and try again')
        return

    print('Finished export to excel, you can view sightings in sightings.xls')
    show_message('Finished export to excel', 'You can view sightings in sightings.xls')

