def clean_parameters(parameter):
    parameter = parameter.lower()

    keepthis = "1234567890abcdefghijklmnopqrstuvwxyz "
    cleaned = ""
    for letter in parameter:
        if letter in keepthis:
            cleaned += letter

    return(cleaned)

# print(clean_parameters("DEFAULT_GENERATED on update CURRENT_TIMESTAMP"))
# print(clean_parameters("on update current_timestamp()"))
