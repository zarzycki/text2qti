import xml.etree.ElementTree as ET
import re
import html
import argparse

def strip_html_tags(text):
    """Remove HTML tags and unescape HTML entities from text."""
    clean = re.compile('<.*?>')  # Regular expression to match HTML tags
    return html.unescape(re.sub(clean, '', text))  # Remove tags and unescape HTML

def parse_qti_to_markdown(qti_file):
    try:
        # Parse the QTI XML file
        tree = ET.parse(qti_file)
        root = tree.getroot()
        namespace = {'qti': 'http://www.imsglobal.org/xsd/ims_qtiasiv1p2'}

        markdown_output = ""

        for section in root.findall('.//qti:section[qti:item]', namespace):
            # Handle each question group (section)
            markdown_output += "\nGROUP\npick: 1\npoints per question: 1\n\n"

            items = section.findall('.//qti:item', namespace)
            for index, item in enumerate(items):
                title = item.get('title', 'Question')
                markdown_output += f"Title: {title}\n"

                # Find the question text
                question_text = item.find('.//qti:mattext', namespace).text
                question_text = strip_html_tags(question_text)
                markdown_output += f"1.  {question_text}\n"

                # Check rcardinality for single or multiple answers
                rcardinality = item.find('.//qti:response_lid', namespace).get('rcardinality', 'Single')

                # Handle feedback text (general feedback)
                feedback = item.find('.//qti:itemfeedback[@ident="general_fb"]//qti:mattext', namespace)
                if feedback is not None:
                    feedback_text = strip_html_tags(feedback.text)
                    markdown_output += f"... {feedback_text}\n"

                # Correct answer identifiers for multiple-answer questions
                correct_answers = [answer.text for answer in item.findall('.//qti:varequal', namespace)]

                # Handle the answer choices
                answer_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  # Labels for options
                for answer_index, response in enumerate(item.findall('.//qti:response_label', namespace)):
                    answer_text = response.find('.//qti:mattext', namespace).text
                    answer_text = strip_html_tags(answer_text)
                    ident = response.get('ident')

                    if rcardinality == "Single":
                        # Single-answer question
                        label = answer_labels[answer_index]
                        if correct_answers and ident in correct_answers:
                            markdown_output += f"*{label})  {answer_text}\n"
                        else:
                            markdown_output += f"{label})  {answer_text}\n"
                    elif rcardinality == "Multiple":
                        # Multiple-answer question
                        if correct_answers and ident in correct_answers:
                            markdown_output += f"[*] {answer_text}\n"
                        else:
                            markdown_output += f"[ ] {answer_text}\n"

                # Add a line break between questions in the group
                markdown_output += "\n"  # Line break between questions

            # Add END_GROUP at the end of the entire group
            markdown_output += "END_GROUP\n\n"

        return markdown_output

    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        try:
            error_line = int(str(e).split(', line ')[1].split(', ')[0])
            with open(qti_file, 'r') as f:
                lines = f.readlines()
                print(f"Error at line {error_line}:")
                print(lines[error_line - 1])
                print(lines[error_line])
                print(lines[error_line + 1])
        except Exception as inner_e:
            print("Unable to extract the line number from the error message.")
            print("Error context could not be determined.")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert QTI XML to Markdown format.")
    parser.add_argument("qti_file", type=str, help="Path to the QTI XML file to be converted.")
    args = parser.parse_args()

    markdown_text = parse_qti_to_markdown(args.qti_file)
    print(markdown_text)
