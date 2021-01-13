import pandas as pd
import re

# filename = "6.008 - Things to Know.txt"
# heading_pattern = r"LN\s\d\d"

# filename = "14-41_ThingsToKnow.txt"
# filename = "CH24-25_14_41-ThingstoKnow.txt"
filename = "CH15-20_14.41-Things to Know.txt"
heading_pattern = r"Ch\d\d"

heading = ""  # tells you lecture note number or something like that

subheading_pattern = r"\d+\.\d+"
subheading = ''

tag = ""

indentation_level = -1
parents = []  # parents of bullet points

def heading2tag(heading):
    rettag = ""
    stop = False
    for chunk in heading.split()[0:2]:
        rettag += chunk
        for s in chunk:
            if s.isdigit():
                stop = True
        if stop:
            break
    return rettag


cols = ["Front", "Back", "pg and ch", "Tags"]
df = pd.DataFrame(columns=cols)

match_dict = {}

match_str = "[0]"
with open(filename, 'r', encoding='utf-8-sig') as f:
    line = "notNone"
    while len(line) > 0:
        back_note = ""

        line = f.readline()
        # if line.startswith('\n') or line.startswith('['):

        match = re.search(r"\[\w{1,3}\]", line)
        if match is not None:
            if match.span()[0] == 0:  # basically if line.startswith(the match)
                if len(match[0]) < len(match_str) or ord(match[0][1]) < ord(match_str[1]):
                    break

            old_line = line
            # line = line[: match.span()[0]] + line[match.span()[1]:]
            match_str = match[0]
            for m in re.findall(r"\[\w{1,3}\]", old_line):
                match_dict[m] = line

        # header
        if re.match(heading_pattern, line) is not None:
            print("header:", line[:-1])
            heading = line
            tag = heading2tag(heading)

        # subheader
        elif line.find('*') == -1 or re.match(subheading_pattern, line) is not None:
            # if the previous item is a subheader and didn't have children
            if not ( line.startswith('\n') or line.startswith('[')) :
                if prev_line == subheading:
                    df = df.append({'Front': subheading, "Back": "", "pg and ch": "", "Tags": tag}, ignore_index=True)

                subheading = line
                print("subheader:", subheading[:-1])

        # finally the questions
        else:
            print("Normal line:", line[:-1])

            if line.find('*') > indentation_level:
                if prev_line is not subheading:
                    parents.append(prev_line)
            elif line.find('*') == indentation_level:
                pass
            elif line.find('*') < indentation_level:
                for par in parents[-1::-1]:
                    if line.find('*') <= par.find('*'):
                        parents.pop()

            item = subheading + ''.join(parents) + line
            df = df.append({'Front': item, "Back": "", "pg and ch": "", "Tags": tag}, ignore_index=True)
            indentation_level = line.find('*')

        prev_line = line

    # dealing with the comments...
    currmatch = match[0]
    curr_comment = ""
    while len(line) > 0:
        match = re.search(r"\[\w{1,3}\]", line)
        if match is not None:
            if len(curr_comment) > 0 and currmatch in match_dict and \
            len(df.Front[df.Front.str.endswith(match_dict[currmatch])]) > 0:
                comment_index = df.Front[df.Front.str.endswith(match_dict[currmatch])].index[0]
                df.Back[comment_index] += (curr_comment + '\n')

            currmatch = match[0]
            curr_comment = line[:match.span()[1]] + '\n' + line[match.span()[1]:]
        else:
            curr_comment += line
        line = f.readline()

    # just to get the last one :)
    if len(curr_comment) > 0 and currmatch in match_dict and \
    len(df.Front[df.Front.str.endswith(match_dict[currmatch])]) > 0:
        comment_index = df.Front[df.Front.str.endswith(match_dict[currmatch])].index[0]
        df.Back[comment_index] += (curr_comment + '\n')

# todo we do not want indices!!!
df = df.sample(frac = 1)
df.to_csv("toANKI_" + ''.join(filename.split()) + '.csv', index=False)

print("happy birthday!")





