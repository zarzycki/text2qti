import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
import uuid

def generate_uuid():
    """Generate a unique identifier."""
    return uuid.uuid4().hex

def create_qti_xml(csv_file, output_file):
    # Define the XML namespaces
    ns = {
        'xmlns': "http://www.imsglobal.org/xsd/ims_qtiasiv1p2",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance"
    }

    # Create the root element
    questestinterop = ET.Element(
        'questestinterop',
        attrib={
            'xmlns': ns['xmlns'],
            'xmlns:xsi': ns['xsi'],
            'xsi:schemaLocation': f"{ns['xmlns']} {ns['xmlns']}/ims_qtiasiv1p2p1.xsd"
        }
    )

    # Create the assessment element
    assessment_id = generate_uuid()
    assessment = ET.SubElement(questestinterop, 'assessment', ident=assessment_id, title='Quiz_Import_Example_Revised2')

    # Add metadata to the assessment
    qtimetadata = ET.SubElement(assessment, 'qtimetadata')
    qtimetadatafield = ET.SubElement(qtimetadata, 'qtimetadatafield')
    ET.SubElement(qtimetadatafield, 'fieldlabel').text = 'cc_maxattempts'
    ET.SubElement(qtimetadatafield, 'fieldentry').text = '1'

    # Create the section element
    section = ET.SubElement(assessment, 'section', ident='root_section')

    # Read the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for index, row in enumerate(reader):
            question_type = row[0]
            points_possible = row[2]
            question_text = row[3]
            correct_answer_index = int(row[4])
            choices = row[5:11]  # Assume choices are in columns 6-11 (inclusive)
            general_fb = row[11]  # Feedback is in column 12 (L)

            # Filter out empty choices
            choices = [choice for choice in choices if choice.strip()]

            # Generate unique identifiers for items and responses
            item_id = generate_uuid()
            response_id = "response1"  # Consistently set response_id to 'response1'

            # Create item (question) element
            item = ET.SubElement(section, 'item', ident=item_id, title=f"Question {index+1}")

            # Add metadata to item
            itemmetadata = ET.SubElement(item, 'itemmetadata')
            qtimetadata = ET.SubElement(itemmetadata, 'qtimetadata')
            qtimetadatafield = ET.SubElement(qtimetadata, 'qtimetadatafield')
            ET.SubElement(qtimetadatafield, 'fieldlabel').text = 'question_type'
            ET.SubElement(qtimetadatafield, 'fieldentry').text = 'multiple_choice_question'
            qtimetadatafield = ET.SubElement(qtimetadata, 'qtimetadatafield')
            ET.SubElement(qtimetadatafield, 'fieldlabel').text = 'points_possible'
            ET.SubElement(qtimetadatafield, 'fieldentry').text = points_possible
            # Additional metadata field
            qtimetadatafield = ET.SubElement(qtimetadata, 'qtimetadatafield')
            ET.SubElement(qtimetadatafield, 'fieldlabel').text = 'assessment_question_identifierref'
            ET.SubElement(qtimetadatafield, 'fieldentry').text = generate_uuid()

            # Create the presentation element
            presentation = ET.SubElement(item, 'presentation')
            material = ET.SubElement(presentation, 'material')
            mattext = ET.SubElement(material, 'mattext', texttype="text/html")
            mattext.text = question_text

            # Create response_lid element with choices
            response_lid = ET.SubElement(presentation, 'response_lid', ident=response_id, rcardinality="Single")
            render_choice = ET.SubElement(response_lid, 'render_choice')

            for choice_index, choice_text in enumerate(choices):
                response_label = ET.SubElement(render_choice, 'response_label', ident=f"{index+1}{choice_index:03d}")
                material = ET.SubElement(response_label, 'material')
                mattext = ET.SubElement(material, 'mattext', texttype="text/plain")
                mattext.text = choice_text

            # Create response processing element
            resprocessing = ET.SubElement(item, 'resprocessing')
            outcomes = ET.SubElement(resprocessing, 'outcomes')
            decvar = ET.SubElement(outcomes, 'decvar', maxvalue="100", minvalue="0", varname="SCORE", vartype="Decimal")

            # Define correct answer
            respcondition = ET.SubElement(resprocessing, 'respcondition', attrib={"continue": "No"})
            conditionvar = ET.SubElement(respcondition, 'conditionvar')
            varequal = ET.SubElement(conditionvar, 'varequal', respident=response_id)
            varequal.text = f"{index+1}{correct_answer_index-1:03d}"
            setvar = ET.SubElement(respcondition, 'setvar', action="Set", varname="SCORE")
            setvar.text = "100"

            # Add general feedback (itemfeedback) only if it exists
            if general_fb.strip():  # Check if the feedback is not an empty string
                itemfeedback = ET.SubElement(item, 'itemfeedback', ident="general_fb")
                flow_mat = ET.SubElement(itemfeedback, 'flow_mat')
                feedback_material = ET.SubElement(flow_mat, 'material')
                feedback_text = ET.SubElement(feedback_material, 'mattext', texttype="text/html")
                feedback_text.text = general_fb

    # Convert the XML to a string
    rough_string = ET.tostring(questestinterop, encoding='ISO-8859-1', xml_declaration=True)

    # Use minidom to beautify the XML string with indentation
    parsed = minidom.parseString(rough_string)
    pretty_xml_as_string = parsed.toprettyxml(indent="  ", encoding='ISO-8859-1')

    # Write the formatted XML string to the output file
    with open(output_file, 'wb') as f:
        f.write(pretty_xml_as_string)

# Example usage
csv_file = 'questions.csv'
output_file = 'output_qti.xml'
create_qti_xml(csv_file, output_file)
print(f"QTI XML generated successfully in {output_file}")
