

import regex as rx
def remove_control_characters(str):
    print(rx.sub(r'\p{C}', '', 'my-string'))
    return rx.sub(r'\p{C}', '', 'my-string')



str="CIGS, ZnS–ZnMgO buffer, Metastability, C– V profiling, SGP"
remove_control_characters(str)
