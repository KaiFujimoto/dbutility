def get_collation(collation):
    string = ""
    for letter in collation:
        if letter == "_":
            break
        else:
            string += letter

    return(string)

print(get_collation("big5_bin"))
