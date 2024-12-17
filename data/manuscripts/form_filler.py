"""
Filling in a form to manage manuscripts and publishing to journals.
"""

FLD_NM = 'field_name'
QSTN = 'question'
OPT = 'optional'
INSTRUCTIONS = 'instructions'
PARAM_TYPE = 'param_type'
QUERY_STR = 'query_string'

def get_form_descr(fld_descrips: list) -> dict:
    descr = {}
    for fld in fld_descrips:
        if fld.get(PARAM_TYPE, '') == QUERY_STR:
            fld_nm = fld[FLD_NM]
            descr[fld_nm] = fld[QSTN]
            if OPT in fld:
                descr[fld_nm] += f'\nOptional: {fld[OPT]}'
    return descr


def get_fld_names(fld_descrips: list) -> list:
    fld_nms = []
    for fld in fld_descrips:
        fld_nms.append(fld[FLD_NM])  # every field MUST have a name!
    return fld_nms


def get_query_fld_names(fld_descrips: list) -> list:
    fld_nms = []
    for fld in fld_descrips:
        if fld.get(PARAM_TYPE, '') == QUERY_STR:
            fld_nms.append(fld[FLD_NM])  # every field MUST have a name!
    return fld_nms
