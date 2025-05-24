from NoteReview import get_worksheet, read_worksheet, parse2dict, recursive_read, parse_blanks

if __name__ == '__main__':
    weight_ = 0.5
    file_lines = ['label start:\n']
    worksheets, sheet_names, poss = get_worksheet(sheet_name='', get_all=True)
    all_layers_hierarchy_ = [read_worksheet(worksheet) for worksheet in worksheets]
    entries_keys = []
    for alh in all_layers_hierarchy_:
        _, top_layer_, top_layer_json_str_ = parse2dict(alh)
        entry_keys = list(top_layer_.keys())
        for entry_key in entry_keys:
            entry_ = top_layer_[entry_key]
            lines_ = recursive_read(entry=entry_)
            lines_with_blanks_, lines_, answers__, contexts_ = parse_blanks(lines=lines_)
            lines_in_a_line = '"{}"\n'.format('\\n'.join([line.strip() for line in lines_]))
            file_lines.append(lines_in_a_line)
    with open(file='script.rpy', mode='w') as f:
        f.writelines(file_lines)
