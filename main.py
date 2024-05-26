#######################
#  Author: NAnglevik  #
#######################

import re


def resolve_references(explanation, parsed_questions):
    referenced_question_match = re.search(r'See (?:the )?explanation (?:of|for) question (\d+\.\d+)', explanation)
    while referenced_question_match:
        referenced_question_id = referenced_question_match.group(1)
        referenced_question = next((q for q in parsed_questions if q['ID'] == referenced_question_id), None)
        if referenced_question:
            referenced_explanation = resolve_references(referenced_question['Explanation'], parsed_questions)
            explanation = explanation.replace(referenced_question_match.group(0), referenced_explanation)
        referenced_question_match = re.search(r'See (?:the )?explanation (?:of|for) question (\d+\.\d+)', explanation)
    return explanation


def parse_text(text):
    # Define regular expressions for extracting information
    question_pattern = re.compile(r'SUR - (\d+\.\d+)\s+(.*?)CLOSE ANSWER AND EXPLANATION ×\s*CLOSE ANSWER AND EXPLANATION ×\s*ANSWER\s*(\w\))\s*(.*?)\s*EXPLANATION\s*(.*?)(?=(?:SUR|$))', re.DOTALL)
    option_pattern = re.compile(r'([A-D])\)\s*(.*?)\s*(?=[A-D]\)|CLOSE)')
    #TODO: handle questions with pattern = "CLOSE ANSWER AND EXPLANATION x 2 ANSWER (no explanation) - E.g.: SUR 5.2"

    # Find all matches in the text
    matches = question_pattern.findall(text)

    # Create a list to store parsed questions
    parsed_questions = []

    # Iterate through matches and extract information
    for match in matches:
        question_id, question, correct_answer, options_text, explanation = match

        # Extract options using the option pattern
        options_matches = option_pattern.findall(options_text)
        options = {option: text.strip() for option, text in options_matches}

        parsed_question = {
            'ID': question_id,
            'Question': question.strip(),
            'Options': options, # options are empty, and therefore not used
            'Correct_Answer': correct_answer.strip(),
            'Explanation': resolve_references(explanation.strip(), parsed_questions),
        }
        parsed_questions.append(parsed_question)

    return parsed_questions

def printAll(parsed_questions):
    # Print the parsed questions
    for question in parsed_questions:
        print(f"ID: {question['ID']}")
        print(f"Question: {question['Question']}")

        for option, text in question['Options'].items():
            print(f"{option}: {text}")

        print(f"Correct Answer: {question['Correct_Answer']}")

        # Exclude specific identifiers from the explanation
        excluded_identifiers = ["CLOSE ANSWER AND EXPLANATION ×", "ANSWER"]
        explanation = question['Explanation']
        for identifier in excluded_identifiers:
            explanation = explanation.replace(identifier, "")

        print(f"Explanation: {explanation.strip()}")
        print("\n" + "-" * 30 + "\n")  # Separating each question


if __name__ == '__main__':
    file_path = "readFile.txt"
    with open(file_path, "r") as file:
        text = file.read().replace(';', ',')

    # Parse the text
    parsed_questions = parse_text(text)
    file.close()

    #printAll(parsed_questions)

    # Generate the Text2Anki file, to be imported into anki
    # The file will be saved as 'writeFile.txt'
    with open('writeFile.txt', 'w', encoding='utf-8') as anki:

        for question in parsed_questions:
            anki.write(question['ID'].strip())
            anki.write("<br>")
            #anki.write(f"Question: {question['Question'].strip()}")

            # format <br> for questions and between options
            temp = question['Question'].strip()
            temp = temp.replace('\n', "<br>")
            index = temp.find("<br>")
            temp2 = temp[:index] + '<br><b>' + temp[index:]
            anki.write(temp2)
            anki.write('<b>')
            #for option, text in question['Options'].items():
            #    anki.write(f"{option}: {text}")

            anki.write(f";{question['Correct_Answer'].strip()}")

            # Exclude specific identifiers from the explanation
            excluded_identifiers = ["CLOSE ANSWER AND EXPLANATION ×", "EXPLANATION", "ANSWER"]
            explanation = question['Explanation']
            for identifier in excluded_identifiers:
                explanation = explanation.replace(identifier, "")

            explanationTemp = explanation.replace('\n', '<br>')
            anki.write(f";{explanationTemp}")
            anki.write("\n")  # Separating each question

    anki.close()


