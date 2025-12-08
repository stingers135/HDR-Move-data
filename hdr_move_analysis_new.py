import os
import re
import xml.etree.ElementTree as ET
import math
import yaml
import json
from datetime import datetime

def _perform_simple_arithmetic(expr_str):
    """
    Helper to perform arithmetic on a string that's guaranteed to be
    numbers and basic operators, with no variables and no nested parentheses
    (parentheses handled by the caller).
    """
    expr_str = expr_str.strip()

    NUMBER_REGEX = r'-?\d+\.?\d*(?:e[+-]?\d+)?'

    while True:
        mult_div_match = re.search(fr'({NUMBER_REGEX})\s*([*/])\s*({NUMBER_REGEX})', expr_str)
        if mult_div_match:
            val1 = float(mult_div_match.group(1))
            operator = mult_div_match.group(2)
            val2 = float(mult_div_match.group(3))
            
            result = 0.0
            if operator == '*':
                result = val1 * val2
            else:
                if val2 == 0:
                    raise ZeroDivisionError("Division by zero in arithmetic evaluation.")
                result = val1 / val2
            
            expr_str = expr_str.replace(mult_div_match.group(0), str(result), 1)
        else:
            break

    while True:
        add_sub_match = re.search(fr'({NUMBER_REGEX})\s*([+-])\s*({NUMBER_REGEX})', expr_str)
        if add_sub_match:
            val1 = float(add_sub_match.group(1))
            operator = add_sub_match.group(2)
            val2 = float(add_sub_match.group(3))
            
            result = 0.0
            if operator == '+':
                result = val1 + val2
            else:
                result = val1 - val2
            
            expr_str = expr_str.replace(add_sub_match.group(0), str(result), 1)
        else:
            break
            
    try:
        return float(expr_str.strip())
    except ValueError:
        return None

def parse_landing_lag_data():
    """Parse landing lag data from fighter_param.prcxml file with fallback location"""
    xml_file_path = r"C:\Users\Alex\Documents\GitHub\HewDraw-Remix\romfs\source\fighter\common\param\fighter_param.prcxml"
    fallback_xml_path = r"C:\Users\Alex\Desktop\smash hacks\fighter_param.xml"
    alt_xml_file_path = "fighter_param.prcxml"
    
    def parse_landing_lag_from_file(xml_path, is_fallback=False):
        """Parse landing lag data from a specific XML file with improved flexibility"""
        xml_to_internal_mapping = {
            'MARIO': 'mario',
            'DONKEY KONG': 'donkey', 
            'LINK': 'link',
            'SAMUS': 'samus',
            'YOSHI': 'yoshi',
            'KIRBY': 'kirby',
            'FOX': 'fox',
            'PIKACHU': 'pikachu',
            'LUIGI': 'luigi',
            'NESS': 'ness',
            'CAPTAIN FALCON': 'captain',
            'JIGGLYPUFF': 'purin',
            'PEACH': 'peach',
            'BOWSER': 'koopa',
            'POPO': 'popo',
            'NANA': 'nana',
            'SHEIK': 'sheik',
            'ZELDA': 'zelda',
            'DR. MARIO': 'mariod',
            'PICHU': 'pichu',
            'FALCO': 'falco',
            'MARTH': 'marth',
            'YOUNG LINK': 'younglink',
            'GANONDORF': 'ganon',
            'MEWTWO': 'mewtwo',
            'ROY': 'roy',
            'MR. GAME & WATCH': 'gamewatch',
            'META KNIGHT': 'metaknight',
            'PIT': 'pit',
            'ZERO SUIT SAMUS': 'szerosuit',
            'WARIO': 'wario',
            'SNAKE': 'snake',
            'IKE': 'ike',
            'SQUIRTLE': 'pzenigame',
            'IVYSAUR': 'pfushigisou',
            'CHARIZARD': 'plizardon',
            'DIDDY KONG': 'diddy',
            'LUCAS': 'lucas',
            'SONIC': 'sonic',
            'KING DEDEDE': 'dedede',
            'OLIMAR': 'pikmin',
            'LUCARIO': 'lucario',
            'R.O.B.': 'robot',
            'TOON LINK': 'toonlink',
            'WOLF': 'wolf',
            'VILLAGER': 'murabito',
            'MEGA MAN': 'rockman',
            'WII FIT TRAINER': 'wiifit',
            'ROSALINA & LUMA': 'rosetta',
            'LITTLE MAC': 'littlemac',
            'GRENINJA': 'gekkouga',
            'PALUTENA': 'palutena',
            'PAC-MAN': 'pacman',
            'ROBIN': 'reflet',
            'SHULK': 'shulk',
            'BOWSER JR.': 'koopajr',
            'DUCK HUNT': 'duckhunt',
            'RYU': 'ryu',
            'CLOUD': 'cloud',
            'CORRIN': 'kamui',
            'BAYONETTA': 'bayonetta',
            'INKLING': 'inkling',
            'RIDLEY': 'ridley',
            'SIMON': 'simon',
            'KING K. ROOL': 'krool',
            'ISABELLE': 'shizue',
            'INCINEROAR': 'gaogaen',
            'PIRANHA PLANT': 'packun',
            'JOKER': 'jack',
            'HERO': 'brave',
            'BANJO & KAZOOIE': 'buddy',
            'TERRY': 'dolly',
            'BYLETH': 'master',
            'MIN MIN': 'tantan',
            'STEVE': 'pickel',
            'KAZUYA': 'demon',
            'SORA': 'trail',
            'PYRA': 'eflame',
            'MYTHRA': 'elight',
            'SEPHIROTH': 'edge',
            'MII BRAWLER': 'miifighter',
            'MII SWORDFIGHTER': 'miiswordsman',
            'MII GUNNER': 'miigunner',
            'DARK SAMUS': 'samusd',
            'DAISY': 'daisy',
            'LUCINA': 'lucina',
            'CHROM': 'chrom',
            'DARK PIT': 'pitb',
            'KEN': 'ken',
            'RICHTER': 'richter'
        }
        
        character_mapping = {
            'mario': 'Mario', 'donkey': 'Donkey Kong', 'link': 'Link', 'samus': 'Samus', 
            'samusd': 'Dark Samus', 'yoshi': 'Yoshi', 'kirby': 'Kirby', 'fox': 'Fox', 
            'pikachu': 'Pikachu', 'luigi': 'Luigi', 'ness': 'Ness', 'captain': 'Captain Falcon', 
            'purin': 'Jigglypuff', 'peach': 'Peach', 'daisy': 'Daisy', 'koopa': 'Bowser', 
            'nana': 'Ice Climbers', 'popo': 'Ice Climbers', 'iceclimber': 'Ice Climbers', 'sheik': 'Sheik', 'zelda': 'Zelda', 
            'mariod': 'Dr.Mario', 'pichu': 'Pichu', 'falco': 'Falco', 'marth': 'Marth', 
            'lucina': 'Lucina', 'younglink': 'Young Link', 'ganon': 'Ganondorf', 'mewtwo': 'Mewtwo', 
            'roy': 'Roy', 'chrom': 'Chrom', 'gamewatch': 'Mr.Game & Watch', 'metaknight': 'Meta Knight', 
            'pit': 'Pit', 'pitb': 'Dark Pit', 'szerosuit': 'Zero Suit Samus', 'wario': 'Wario', 
            'snake': 'Snake', 'ike': 'Ike', 'pzenigame': 'Squirtle', 'pfushigisou': 'Ivysaur', 
            'plizardon': 'Charizard', 'diddy': 'Diddy Kong', 'lucas': 'Lucas', 'sonic': 'Sonic', 
            'dedede': 'King Dedede', 'pikmin': 'Olimar', 'lucario': 'Lucario', 'robot': 'R.O.B.', 
            'toonlink': 'Toon Link', 'wolf': 'Wolf', 'murabito': 'Villager', 'rockman': 'Mega Man', 
            'wiifit': 'Wii Fit Trainer', 'rosetta': 'Rosalina & Luma', 'littlemac': 'Little Mac', 
            'gekkouga': 'Greninja', 'miifighter': 'Mii Brawler', 'miiswordsman': 'Mii Swordfighter', 
            'miigunner': 'Mii Gunner', 'palutena': 'Palutena', 'pacman': 'Pac-Man', 'reflet': 'Robin', 
            'shulk': 'Shulk', 'koopajr': 'Bowser Jr.', 'duckhunt': 'Duck Hunt', 'ryu': 'Ryu', 
            'ken': 'Ken', 'cloud': 'Cloud', 'kamui': 'Corrin', 'bayonetta': 'Bayonetta', 
            'inkling': 'Inkling', 'ridley': 'Ridley', 'simon': 'Simon', 'richter': 'Richter', 
            'krool': 'King K. Rool', 'shizue': 'Isabelle', 'gaogaen': 'Incineroar', 'packun': 'Piranha Plant', 
            'jack': 'Joker', 'brave': 'Hero', 'buddy': 'Banjo & Kazooie', 'dolly': 'Terry', 
            'master': 'Byleth', 'tantan': 'Min Min', 'pickel': 'Steve', 'edge': 'Sephiroth', 
            'eflame': 'Pyra', 'element': 'Rex', 'elight': 'Mythra', 'demon': 'Kazuya', 'trail': 'Sora'
        }
        
        landing_lag_data = {}
        
        try:
            with open(xml_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            fighter_list = root.find('.//list[@hash="fighter_param_table"]')
            if fighter_list is None:
                if is_fallback:
                    print(f"Warning: Could not find fighter_param_table in fallback XML")
                return {}
            
            structs = fighter_list.findall('struct')
            
            struct_by_index = {}
            for struct in structs:
                index_attr = struct.get('index')
                if index_attr is not None:
                    struct_by_index[int(index_attr)] = struct
            
            comment_to_struct_mapping = {}
            
            strict_pattern = r'<!--\s*([^-]+?)\s*-->\s*<struct index="(\d+)"'
            strict_matches = re.findall(strict_pattern, content, re.MULTILINE | re.DOTALL)
            
            for char_name, struct_index in strict_matches:
                char_name_clean = char_name.strip()
                comment_to_struct_mapping[char_name_clean] = int(struct_index)
            
            flexible_pattern = r'<!--\s*([^-]+?)\s*-->[\s\S]*?<struct index="(\d+)"'
            flexible_matches = re.findall(flexible_pattern, content, re.MULTILINE | re.DOTALL)
            
            for char_name, struct_index in flexible_matches:
                char_name_clean = char_name.strip()
                if char_name_clean not in comment_to_struct_mapping:
                    comment_pos = content.find(f'<!-- {char_name_clean} -->')
                    if comment_pos == -1:
                        comment_pos = content.find(f'<!--{char_name_clean}-->')
                    struct_pos = content.find(f'<struct index="{struct_index}"')
                    
                    if comment_pos != -1 and struct_pos != -1:
                        distance = struct_pos - comment_pos
                        if 0 < distance < 2000:
                            comment_to_struct_mapping[char_name_clean] = int(struct_index)
            
            file_label = "FALLBACK" if is_fallback else "PRIMARY"
            
            pacman_found = False
            for char_name in comment_to_struct_mapping.keys():
                if 'PAC' in char_name:
                    pacman_found = True
            
            if not pacman_found:
                pac_comment_pos = content.find('<!-- PAC-MAN -->')
                if pac_comment_pos != -1:
                    remaining_content = content[pac_comment_pos:]
                    next_struct_match = re.search(r'<struct index="(\d+)"', remaining_content)
                    if next_struct_match:
                        struct_index = int(next_struct_match.group(1))
                        distance = next_struct_match.start()
                        comment_to_struct_mapping['PAC-MAN'] = struct_index
                else:
                    print(f"DEBUG {file_label}: PAC-MAN comment not found at all")
            
            strict_pattern = r'<!--\s*([^-]+?)\s*-->\s*<struct index="(\d+)"'
            strict_matches = re.findall(strict_pattern, content, re.MULTILINE | re.DOTALL)
            
            flexible_pattern = r'<!--\s*([^-]+?)\s*-->[\s\S]*?<struct index="(\d+)"'
            flexible_matches = re.findall(flexible_pattern, content, re.MULTILINE | re.DOTALL)
            
            for char_name, struct_index in strict_matches:
                char_name_clean = char_name.strip()
                comment_to_struct_mapping[char_name_clean] = int(struct_index)
            
            for char_name, struct_index in flexible_matches:
                char_name_clean = char_name.strip()
                if char_name_clean not in comment_to_struct_mapping:
                    comment_pos = content.find(f'<!-- {char_name_clean} -->')
                    struct_pos = content.find(f'<struct index="{struct_index}"')
                    if comment_pos != -1 and struct_pos != -1:
                        distance = struct_pos - comment_pos
                        if 0 < distance < 1000:
                            comment_to_struct_mapping[char_name_clean] = int(struct_index)
            
            for char_name_xml, struct_index in comment_to_struct_mapping.items():
                    
                if char_name_xml in ['GIGA BOWSER', 'MII BRAWLER (FIGHTING TEAM)', 'MII SWORDFIGHTER (FIGHTING TEAM)', 'MII GUNNER (FIGHTING TEAM)']:
                    continue
                
                internal_name = xml_to_internal_mapping.get(char_name_xml)
                if not internal_name:
                    if is_fallback:
                        print(f"Fallback: Unknown character in XML: {char_name_xml}")
                    continue
                
                display_name = character_mapping.get(internal_name)
                if not display_name:
                    if is_fallback:
                        print(f"Fallback: No display name for internal name: {internal_name}")
                    continue
                
                struct = struct_by_index.get(struct_index)
                if struct is None:
                    if is_fallback:
                        print(f"Fallback: Could not find struct with index {struct_index} for {char_name_xml}")
                    continue
                
                landing_lag = {}
                
                lag_mappings = {
                    'landing_attack_air_frame_n': 'nair',
                    'landing_attack_air_frame_f': 'fair', 
                    'landing_attack_air_frame_b': 'bair',
                    'landing_attack_air_frame_hi': 'uair',
                    'landing_attack_air_frame_lw': 'dair'
                }
                
                for hash_name, move_type in lag_mappings.items():
                    element = struct.find(f'.//float[@hash="{hash_name}"]')
                    if element is not None:
                        try:
                            value = int(float(element.text))
                            landing_lag[move_type] = value
                                
                        except (ValueError, TypeError):
                            landing_lag[move_type] = 0
                    else:
                        landing_lag[move_type] = 0
            
                landing_lag_data[display_name] = landing_lag

            return landing_lag_data
            
        except Exception as e:
            if is_fallback:
                print(f"Error parsing fallback landing lag data: {e}")
            else:
                print(f"Error parsing primary landing lag data: {e}")
            return {}
    
    primary_xml_path = None
    if os.path.exists(xml_file_path):
        primary_xml_path = xml_file_path
    elif os.path.exists(alt_xml_file_path):
        primary_xml_path = alt_xml_file_path
    else:
        print(f"Warning: Could not find primary fighter_param.xml file")
        primary_xml_path = None
    
    primary_data = {}
    if primary_xml_path:
        primary_data = parse_landing_lag_from_file(primary_xml_path, is_fallback=False)
    
    fallback_data = {}
    if os.path.exists(fallback_xml_path):
        fallback_data = parse_landing_lag_from_file(fallback_xml_path, is_fallback=True)
    else:
        print(f"Fallback file not found at: {fallback_xml_path}")
    
    final_data = primary_data.copy()
    
    moves_replaced = 0
    characters_affected = 0
    
    for char_name in final_data:
        if char_name in fallback_data:
            primary_lag_data = final_data[char_name]
            fallback_lag_data = fallback_data[char_name]
            
            character_had_replacements = False
            
            for move_type in ['nair', 'fair', 'bair', 'uair', 'dair']:
                primary_value = primary_lag_data.get(move_type, 0)
                fallback_value = fallback_lag_data.get(move_type, 0)
                
                if primary_value == 0 and fallback_value > 0:
                    final_data[char_name][move_type] = fallback_value
                    moves_replaced += 1
                    character_had_replacements = True
            
            if character_had_replacements:
                characters_affected += 1
    
    for char_name, fallback_lag_data in fallback_data.items():
        if char_name not in final_data:
            final_data[char_name] = fallback_lag_data
            characters_affected += 1
    return final_data

def parse_fighter_stats_data():
    """Parse fighter stats data from fighter_param.prcxml file with fallback location"""
    xml_file_path = r"C:\Users\Alex\Documents\GitHub\HewDraw-Remix\romfs\source\fighter\common\param\fighter_param.prcxml"
    fallback_xml_path = r"C:\Users\Alex\Desktop\smash hacks\fighter_param.xml"
    alt_xml_file_path = "fighter_param.prcxml"
    
    def parse_fighter_stats_from_file(xml_path, is_fallback=False):
        """Parse fighter stats data from a specific XML file"""
        xml_to_internal_mapping = {
            'MARIO': 'mario',
            'DONKEY KONG': 'donkey', 
            'LINK': 'link',
            'SAMUS': 'samus',
            'YOSHI': 'yoshi',
            'KIRBY': 'kirby',
            'FOX': 'fox',
            'PIKACHU': 'pikachu',
            'LUIGI': 'luigi',
            'NESS': 'ness',
            'CAPTAIN FALCON': 'captain',
            'JIGGLYPUFF': 'purin',
            'PEACH': 'peach',
            'BOWSER': 'koopa',
            'POPO': 'popo',
            'NANA': 'nana',
            'SHEIK': 'sheik',
            'ZELDA': 'zelda',
            'DR. MARIO': 'mariod',
            'PICHU': 'pichu',
            'FALCO': 'falco',
            'MARTH': 'marth',
            'YOUNG LINK': 'younglink',
            'GANONDORF': 'ganon',
            'MEWTWO': 'mewtwo',
            'ROY': 'roy',
            'MR. GAME & WATCH': 'gamewatch',
            'META KNIGHT': 'metaknight',
            'PIT': 'pit',
            'ZERO SUIT SAMUS': 'szerosuit',
            'WARIO': 'wario',
            'SNAKE': 'snake',
            'IKE': 'ike',
            'SQUIRTLE': 'pzenigame',
            'IVYSAUR': 'pfushigisou',
            'CHARIZARD': 'plizardon',
            'DIDDY KONG': 'diddy',
            'LUCAS': 'lucas',
            'SONIC': 'sonic',
            'KING DEDEDE': 'dedede',
            'OLIMAR': 'pikmin',
            'LUCARIO': 'lucario',
            'R.O.B.': 'robot',
            'TOON LINK': 'toonlink',
            'WOLF': 'wolf',
            'VILLAGER': 'murabito',
            'MEGA MAN': 'rockman',
            'WII FIT TRAINER': 'wiifit',
            'ROSALINA & LUMA': 'rosetta',
            'LITTLE MAC': 'littlemac',
            'GRENINJA': 'gekkouga',
            'PALUTENA': 'palutena',
            'PAC-MAN': 'pacman',
            'ROBIN': 'reflet',
            'SHULK': 'shulk',
            'BOWSER JR.': 'koopajr',
            'DUCK HUNT': 'duckhunt',
            'RYU': 'ryu',
            'CLOUD': 'cloud',
            'CORRIN': 'kamui',
            'BAYONETTA': 'bayonetta',
            'INKLING': 'inkling',
            'RIDLEY': 'ridley',
            'SIMON': 'simon',
            'KING K. ROOL': 'krool',
            'ISABELLE': 'shizue',
            'INCINEROAR': 'gaogaen',
            'PIRANHA PLANT': 'packun',
            'JOKER': 'jack',
            'HERO': 'brave',
            'BANJO & KAZOOIE': 'buddy',
            'TERRY': 'dolly',
            'BYLETH': 'master',
            'MIN MIN': 'tantan',
            'STEVE': 'pickel',
            'KAZUYA': 'demon',
            'SORA': 'trail',
            'PYRA': 'eflame',
            'MYTHRA': 'elight',
            'SEPHIROTH': 'edge',
            'MII BRAWLER': 'miifighter',
            'MII SWORDFIGHTER': 'miiswordsman',
            'MII GUNNER': 'miigunner',
            'DARK SAMUS': 'samusd',
            'DAISY': 'daisy',
            'LUCINA': 'lucina',
            'CHROM': 'chrom',
            'DARK PIT': 'pitb',
            'KEN': 'ken',
            'RICHTER': 'richter'
        }
        
        character_mapping = {
            'mario': 'Mario', 'donkey': 'Donkey Kong', 'link': 'Link', 'samus': 'Samus', 
            'samusd': 'Dark Samus', 'yoshi': 'Yoshi', 'kirby': 'Kirby', 'fox': 'Fox', 
            'pikachu': 'Pikachu', 'luigi': 'Luigi', 'ness': 'Ness', 'captain': 'Captain Falcon', 
            'purin': 'Jigglypuff', 'peach': 'Peach', 'daisy': 'Daisy', 'koopa': 'Bowser', 
            'nana': 'Ice Climbers', 'popo': 'Ice Climbers', 'iceclimber': 'Ice Climbers', 'sheik': 'Sheik', 'zelda': 'Zelda', 
            'mariod': 'Dr.Mario', 'pichu': 'Pichu', 'falco': 'Falco', 'marth': 'Marth', 
            'lucina': 'Lucina', 'younglink': 'Young Link', 'ganon': 'Ganondorf', 'mewtwo': 'Mewtwo', 
            'roy': 'Roy', 'chrom': 'Chrom', 'gamewatch': 'Mr.Game & Watch', 'metaknight': 'Meta Knight', 
            'pit': 'Pit', 'pitb': 'Dark Pit', 'szerosuit': 'Zero Suit Samus', 'wario': 'Wario', 
            'snake': 'Snake', 'ike': 'Ike', 'pzenigame': 'Squirtle', 'pfushigisou': 'Ivysaur', 
            'plizardon': 'Charizard', 'diddy': 'Diddy Kong', 'lucas': 'Lucas', 'sonic': 'Sonic', 
            'dedede': 'King Dedede', 'pikmin': 'Olimar', 'lucario': 'Lucario', 'robot': 'R.O.B.', 
            'toonlink': 'Toon Link', 'wolf': 'Wolf', 'murabito': 'Villager', 'rockman': 'Mega Man', 
            'wiifit': 'Wii Fit Trainer', 'rosetta': 'Rosalina & Luma', 'littlemac': 'Little Mac', 
            'gekkouga': 'Greninja', 'miifighter': 'Mii Brawler', 'miiswordsman': 'Mii Swordfighter', 
            'miigunner': 'Mii Gunner', 'palutena': 'Palutena', 'pacman': 'Pac-Man', 'reflet': 'Robin', 
            'shulk': 'Shulk', 'koopajr': 'Bowser Jr.', 'duckhunt': 'Duck Hunt', 'ryu': 'Ryu', 
            'ken': 'Ken', 'cloud': 'Cloud', 'kamui': 'Corrin', 'bayonetta': 'Bayonetta', 
            'inkling': 'Inkling', 'ridley': 'Ridley', 'simon': 'Simon', 'richter': 'Richter', 
            'krool': 'King K. Rool', 'shizue': 'Isabelle', 'gaogaen': 'Incineroar', 'packun': 'Piranha Plant', 
            'jack': 'Joker', 'brave': 'Hero', 'buddy': 'Banjo & Kazooie', 'dolly': 'Terry', 
            'master': 'Byleth', 'tantan': 'Min Min', 'pickel': 'Steve', 'edge': 'Sephiroth', 
            'eflame': 'Pyra', 'element': 'Rex', 'elight': 'Mythra', 'demon': 'Kazuya', 'trail': 'Sora'
        }
        
        fighter_stats_data = {}
        
        try:
            with open(xml_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            fighter_list = root.find('.//list[@hash="fighter_param_table"]')
            if fighter_list is None:
                if is_fallback:
                    print(f"Warning: Could not find fighter_param_table in fallback XML")
                return {}
            
            structs = fighter_list.findall('struct')
            
            struct_by_index = {}
            for struct in structs:
                index_attr = struct.get('index')
                if index_attr is not None:
                    struct_by_index[int(index_attr)] = struct
            
            comment_to_struct_mapping = {}
            
            strict_pattern = r'<!--\s*([^-]+?)\s*-->\s*<struct index="(\d+)"'
            strict_matches = re.findall(strict_pattern, content, re.MULTILINE | re.DOTALL)
            
            for char_name, struct_index in strict_matches:
                char_name_clean = char_name.strip()
                comment_to_struct_mapping[char_name_clean] = int(struct_index)
            
            flexible_pattern = r'<!--\s*([^-]+?)\s*-->[\s\S]*?<struct index="(\d+)"'
            flexible_matches = re.findall(flexible_pattern, content, re.MULTILINE | re.DOTALL)
            
            for char_name, struct_index in flexible_matches:
                char_name_clean = char_name.strip()
                if char_name_clean not in comment_to_struct_mapping:
                    comment_pos = content.find(f'<!-- {char_name_clean} -->')
                    if comment_pos == -1:
                        comment_pos = content.find(f'<!--{char_name_clean}-->')
                    struct_pos = content.find(f'<struct index="{struct_index}"')
                    
                    if comment_pos != -1 and struct_pos != -1:
                        distance = struct_pos - comment_pos
                        if 0 < distance < 2000:
                            comment_to_struct_mapping[char_name_clean] = int(struct_index)
            
            pacman_found = False
            for char_name in comment_to_struct_mapping.keys():
                if 'PAC' in char_name:
                    pacman_found = True

            if not pacman_found:
                pac_comment_pos = content.find('<!-- PAC-MAN -->')
                if pac_comment_pos != -1:
                    remaining_content = content[pac_comment_pos:]
                    next_struct_match = re.search(r'<struct index="(\d+)"', remaining_content)
                    if next_struct_match:
                        struct_index = int(next_struct_match.group(1))
                        comment_to_struct_mapping['PAC-MAN'] = struct_index
            
            for char_name_xml, struct_index in comment_to_struct_mapping.items():
                    
                if char_name_xml in ['GIGA BOWSER', 'MII BRAWLER (FIGHTING TEAM)', 'MII SWORDFIGHTER (FIGHTING TEAM)', 'MII GUNNER (FIGHTING TEAM)']:
                    continue
                
                internal_name = xml_to_internal_mapping.get(char_name_xml)
                if not internal_name:
                    if is_fallback:
                        print(f"Fallback: Unknown character in XML: {char_name_xml}")
                    continue
                
                display_name = character_mapping.get(internal_name)
                if not display_name:
                    if is_fallback:
                        print(f"Fallback: No display name for internal name: {internal_name}")
                    continue
                
                struct = struct_by_index.get(struct_index)
                if struct is None:
                    if is_fallback:
                        print(f"Fallback: Could not find struct with index {struct_index} for {char_name_xml}")
                    continue
                
                fighter_stats = {}
                
                stats_mappings = {
                    'walk_speed_max': 'walk_speed',
                    'run_speed_max': 'run_speed',
                    'dash_speed': 'dash_speed',
                    'weight': 'weight',
                    'jump_squat_frame': 'jumpsquat',
                    'jump_speed_x_max': 'jump_speed_x_max',
                    'jump_y': 'full_hop',
                    'mini_jump_y': 'short_hop',
                    'jump_aerial_y': 'double_jump',
                    'air_speed_y_stable': 'fall_speed',
                    'air_accel_y': 'gravity',
                    'air_accel_x_mul': 'air_accel_x_mul',
                    'air_accel_x_add': 'air_accel_x_add',
                    'air_speed_x_stable': 'max_air_speed'
                }
                
                for hash_name, stat_type in stats_mappings.items():
                    element = struct.find(f'.//*[@hash="{hash_name}"]')
                    if element is not None:
                        try:
                            if element.tag == 'int':
                                value = int(element.text)
                            else:
                                value = float(element.text)
                            fighter_stats[stat_type] = value
                                
                        except (ValueError, TypeError):
                            fighter_stats[stat_type] = None
                    else:
                        fighter_stats[stat_type] = None

                fighter_stats_data[display_name] = fighter_stats

            return fighter_stats_data
            
        except Exception as e:
            if is_fallback:
                print(f"Error parsing fallback fighter stats data: {e}")
            else:
                print(f"Error parsing primary fighter stats data: {e}")
            return {}
    
    primary_xml_path = None
    if os.path.exists(xml_file_path):
        primary_xml_path = xml_file_path
    elif os.path.exists(alt_xml_file_path):
        primary_xml_path = alt_xml_file_path
    else:
        print(f"Warning: Could not find primary fighter_param.xml file")
        primary_xml_path = None
    
    primary_data = {}
    if primary_xml_path:
        primary_data = parse_fighter_stats_from_file(primary_xml_path, is_fallback=False)
    
    fallback_data = {}
    if os.path.exists(fallback_xml_path):
        fallback_data = parse_fighter_stats_from_file(fallback_xml_path, is_fallback=True)
    else:
        print(f"Fallback file not found at: {fallback_xml_path}")
    
    final_data = primary_data.copy()
    
    stats_replaced = 0
    characters_affected = 0
    
    for char_name in final_data:
        if char_name in fallback_data:
            primary_stats_data = final_data[char_name]
            fallback_stats_data = fallback_data[char_name]
            
            character_had_replacements = False
            
            for stat_type in ['walk_speed', 'run_speed', 'dash_speed', 'weight', 'jumpsquat', 'jump_speed_x_max', 'full_hop', 'short_hop', 'double_jump', 'fall_speed', 'gravity', 'air_accel_x_mul', 'air_accel_x_add', 'max_air_speed']:
                primary_value = primary_stats_data.get(stat_type)
                fallback_value = fallback_stats_data.get(stat_type)
                
                if primary_value is None and fallback_value is not None:
                    final_data[char_name][stat_type] = fallback_value
                    stats_replaced += 1
                    character_had_replacements = True
            
            if character_had_replacements:
                characters_affected += 1
    
    for char_name in final_data:
        char_stats = final_data[char_name]
        mul_val = char_stats.get('air_accel_x_mul')
        add_val = char_stats.get('air_accel_x_add')
        
        if mul_val is not None and add_val is not None:
            char_stats['air_acceleration'] = mul_val + add_val
        else:
            char_stats['air_acceleration'] = None

    return final_data

def extract_steve_dair_frame_from_fallback():
    """Extract frame data for Steve's dair from fallback location"""
    fallback_base_path = r"C:\Users\Alex\Documents\GitHub\Roy\SSBU-Dumped-Scripts\smashline-hdr"
    
    possible_paths = [
        os.path.join(fallback_base_path, "lua2cpp_pickel", "pickel"),
        os.path.join(fallback_base_path, "lua2cpp_pickel"),
        os.path.join(fallback_base_path, "pickel"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            fallback_file_path = os.path.join(path, "AttackAirLw.txt")
            
            if os.path.exists(fallback_file_path):
                try:
                    with open(fallback_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                    
                    lines = content.split('\n')
                    current_frame = 0.0
                    
                    for line in lines:
                        line = line.strip()
                        
                        if 'frame(' in line and 'lua_state' in line:
                            frame_pattern = r'frame\s*\(\s*lua_state\s*,\s*([0-9.]+)\s*\)'
                            match = re.search(frame_pattern, line)
                            if match:
                                current_frame = float(match.group(1))
                        
                        if '*FIGHTER_PICKEL_STATUS_ATTACK_FLAG_FORGE_GENERATE_ENABLE' in line:
                            return current_frame
                            
                except Exception as e:
                    print(f"Error reading Steve dair fallback file {fallback_file_path}: {e}")
    
    return 12.0
    
def extract_steve_dsmash_frame_from_fallback():
    """Extract frame data for Steve's dsmash from fallback location"""
    fallback_base_path = r"C:\Users\Alex\Documents\GitHub\Roy\SSBU-Dumped-Scripts\smashline-hdr"
    
    possible_paths = [
        os.path.join(fallback_base_path, "lua2cpp_pickel", "pickel"),
        os.path.join(fallback_base_path, "lua2cpp_pickel"),
        os.path.join(fallback_base_path, "pickel"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            fallback_file_path = os.path.join(path, "AttackLw4.txt")
            
            if os.path.exists(fallback_file_path):
                try:
                    with open(fallback_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                    
                    lines = content.split('\n')
                    current_frame = 0.0
                    
                    for line in lines:
                        line = line.strip()
                        
                        if 'frame(' in line and 'lua_state' in line:
                            frame_pattern = r'frame\s*\(\s*lua_state\s*,\s*([0-9.]+)\s*\)'
                            match = re.search(frame_pattern, line)
                            if match:
                                current_frame = float(match.group(1))
                        
                        if 'ArticleModule::generate_article' in line and '*FIGHTER_PICKEL_GENERATE_ARTICLE_MELT' in line:
                            return current_frame
                            
                except Exception as e:
                    print(f"Error reading Steve dsmash fallback file {fallback_file_path}: {e}")
    
    return 8.0

def get_numerical_value(param_string, original_variable_values):
    """
    Helper to resolve a parameter string to a numerical value, handling variables and arithmetic expressions.
    """
    variable_values = {var: str(val) for var, val in original_variable_values.items()}
    
    resolved_vars_cache = {}

    max_iterations = 100
    for _ in range(max_iterations):
        made_substitution = False
        
        for var_name, var_value_str_raw in list(variable_values.items()): 
            if var_name in resolved_vars_cache:
                continue

            current_var_value_for_eval = re.sub(r'//.*$', '', var_value_str_raw).strip()
            for r_var, r_val in resolved_vars_cache.items():
                 current_var_value_for_eval = re.sub(r'\b' + re.escape(r_var) + r'\b', str(r_val), current_var_value_for_eval)

            needs_further_resolution = False
            for other_var_name in variable_values.keys():
                if other_var_name != var_name and other_var_name not in resolved_vars_cache and re.search(r'\b' + re.escape(other_var_name) + r'\b', current_var_value_for_eval):
                    needs_further_resolution = True
                    break
            
            if needs_further_resolution:
                continue

            try:
                resolved_val = _perform_simple_arithmetic(current_var_value_for_eval)
                
                if resolved_val is not None:
                    resolved_vars_cache[var_name] = resolved_val
                    made_substitution = True
            except Exception:
                pass

        if not made_substitution:
            break
    
    resolved_param_string = str(param_string).strip()
    resolved_param_string = re.sub(r'//.*$', '', resolved_param_string).strip()

    for r_var, r_val in resolved_vars_cache.items():
        resolved_param_string = re.sub(r'\b' + re.escape(r_var) + r'\b', str(r_val), resolved_param_string)
    
    try:
        current_expression_to_evaluate = resolved_param_string
        while '(' in current_expression_to_evaluate:
            innermost_paren_match = re.search(r'\(([^()]+)\)', current_expression_to_evaluate)
            if innermost_paren_match:
                inner_expr = innermost_paren_match.group(1)
                resolved_inner_value = _perform_simple_arithmetic(inner_expr)
                if resolved_inner_value is not None:
                    current_expression_to_evaluate = current_expression_to_evaluate.replace(innermost_paren_match.group(0), str(resolved_inner_value), 1)
                else:
                    return None
            else:
                break

        final_value = _perform_simple_arithmetic(current_expression_to_evaluate)
        if final_value is not None:
            return final_value
            
    except (TypeError, SyntaxError, KeyError, ZeroDivisionError, ValueError) as e:
        pass

    try:
        numerical_match = re.search(r'(-?[0-9]+\.?[0-9]*(?:e[+-]?\d+)?)', param_string) 
        if numerical_match:
            fallback_val = float(numerical_match.group(1))
            return fallback_val
    except ValueError:
        pass
    
    return None
    
def get_numerical_value_enhanced(param_string, variable_values, pikmin_multipliers=None):
    """
    For pikmin stuff.
    """
    param_string = str(param_string).strip()
    
    param_string = re.sub(r'//.*$', '', param_string).strip()
    
    if pikmin_multipliers and 'p.' in param_string:
        if 'p.dmg' in param_string:
            param_string = param_string.replace('p.dmg', str(pikmin_multipliers.get('dmg', 1.05)))
        
        if 'p.angle' in param_string:
            param_string = param_string.replace('p.angle', str(pikmin_multipliers.get('angle', 0)))
    
    return get_numerical_value(param_string, variable_values)

def calculate_total_throw_damage(function_body, variable_values, character_internal_name, move_type):
    """
    Calculate total damage for throws by summing all hitboxes that will land, with character exceptions for non-connecting hitboxes.
    Also includes damage from articles generated during throws (e.g., Mewtwo's shadowballs).
    """
    
    lines = function_body.split('\n')
    total_damage = 0.0
    current_frame = 0.0
    
    throw_attacks = []
    regular_attacks = []
    article_damage = 0.0
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if 'frame(' in line and ('lua_state' in line or 'agent.lua_state_agent' in line):
            frame_pattern = r'frame\s*\(\s*(?:lua_state|agent\.lua_state_agent)\s*,\s*([0-9.]+)\s*\)'
            match = re.search(frame_pattern, line)
            if match:
                current_frame = float(match.group(1))
        
        if 'wait(' in line and 'lua_state' in line:
            wait_pattern = r'wait\s*\(\s*lua_state\s*,\s*([0-9.]+)\s*\)'
            match = re.search(wait_pattern, line)
            if match:
                current_frame += float(match.group(1))
        
        if 'ArticleModule::generate_article' in line:
            article_damage_contribution = extract_article_damage_for_throw(line, character_internal_name, move_type)
            if article_damage_contribution:
                article_damage += article_damage_contribution

        if 'for ' in line and ' in 0..' in line:
            loop_match = re.search(r'for\s+\w+\s+in\s+0\.\.(\d+)', line)
            if loop_match:
                loop_iterations = int(loop_match.group(1))
                
                loop_body = []
                brace_count = 1
                j = i + 1
                
                while j < len(lines) and brace_count > 0:
                    loop_line = lines[j]
                    loop_body.append(loop_line)
                    brace_count += loop_line.count('{')
                    brace_count -= loop_line.count('}')
                    j += 1
                
                found_attack_in_loop = False
                for loop_line in loop_body:
                    if 'ATTACK(agent,' in loop_line and not loop_line.strip().startswith('//'):
                        if not found_attack_in_loop:
                            damage = extract_throw_attack_damage(loop_line, variable_values, character_internal_name)
                            if damage:
                                total_damage += damage * loop_iterations
                                found_attack_in_loop = True
                    elif 'ArticleModule::generate_article' in loop_line:
                        loop_article_damage = extract_article_damage_for_throw(loop_line, character_internal_name, move_type)
                        if loop_article_damage:
                            article_damage += loop_article_damage * loop_iterations
                
                i = j - 1
                i += 1
                continue
        
        if 'ATTACK_ABS' in line and '*FIGHTER_ATTACK_ABSOLUTE_KIND_THROW' in line:
            damage = extract_attack_abs_throw_damage(line, variable_values)
            if damage:
                throw_attacks.append((damage, current_frame, line))
        
        elif 'ATTACK(agent,' in line and not line.startswith('//'):
            damage = extract_throw_attack_damage(line, variable_values, character_internal_name)
            if damage:
                regular_attacks.append((damage, current_frame, line))
        
        i += 1
    
    if throw_attacks:
        if character_internal_name == 'pikmin':
            total_damage += throw_attacks[0][0]
        elif character_internal_name == 'pichu' and len(throw_attacks) == 2:
            damages = [attack[0] for attack in throw_attacks]
            total_damage += min(damages)
        elif character_internal_name == 'gaogaen' and len(throw_attacks) > 1:
            damages = [attack[0] for attack in throw_attacks]
            total_damage += min(damages)
        elif len(throw_attacks) > 1:
            total_damage += throw_attacks[0][0]
        else:
            total_damage += throw_attacks[0][0]
    
    if regular_attacks:
        if character_internal_name == 'metaknight' and move_type == 'fthrow':
            if len(regular_attacks) >= 2:
                regular_attacks_sorted = sorted(regular_attacks, key=lambda x: x[1])
                total_damage += regular_attacks_sorted[0][0]
            elif len(regular_attacks) == 1:
                total_damage += regular_attacks[0][0]
                
        elif character_internal_name == 'demon':
            
            has_conditional_branches = 'PostureModule::scale' in function_body
            has_multiple_frame_groups = len(set(attack[1] for attack in regular_attacks)) >= 3 if regular_attacks else False
            
            if has_conditional_branches and has_multiple_frame_groups:
                
                attacks_by_frame = {}
                for damage, frame, line in regular_attacks:
                    if frame not in attacks_by_frame:
                        attacks_by_frame[frame] = []
                    attacks_by_frame[frame].append((damage, frame, line))
                
                sorted_frames = sorted(attacks_by_frame.keys())
                
                for frame in sorted_frames[:-1]:
                    if attacks_by_frame[frame]:
                        total_damage += attacks_by_frame[frame][0][0]
            else:
                frame_attacks = {}
                for damage, frame, line in regular_attacks:
                    if frame not in frame_attacks:
                        frame_attacks[frame] = damage
                
                for frame_damage in frame_attacks.values():
                    total_damage += frame_damage
                    
        elif character_internal_name == 'ryu':
            pass
        elif character_internal_name == 'gaogaen':
            has_revenge_conditionals = 'IS_HEAVY_ATTACK' in function_body
            
            if has_revenge_conditionals and len(regular_attacks) > 1:
                frame_attacks = {}
                for damage, frame, line in regular_attacks:
                    if frame not in frame_attacks:
                        frame_attacks[frame] = []
                    frame_attacks[frame].append(damage)
                
                for frame, damages in frame_attacks.items():
                    total_damage += min(damages)
            else:
                frame_attacks = {}
                for damage, frame, line in regular_attacks:
                    if frame not in frame_attacks:
                        frame_attacks[frame] = damage
                
                for frame_damage in frame_attacks.values():
                    total_damage += frame_damage    
        elif character_internal_name == 'pichu' and len(regular_attacks) == 2:
            damages = [attack[0] for attack in regular_attacks]
            total_damage += min(damages)
        else:
            frame_attacks = {}
            for damage, frame, line in regular_attacks:
                if frame not in frame_attacks:
                    frame_attacks[frame] = damage
            
            for frame_damage in frame_attacks.values():
                total_damage += frame_damage
    
    total_damage += article_damage
    
    return total_damage

def extract_article_damage_for_throw(line, character_internal_name, move_type):
    """Extract damage contribution from ArticleModule::generate_article calls during throws"""
    
    article_damage_mapping = {
        ('mewtwo', 'FIGHTER_MEWTWO_GENERATE_ARTICLE_SHADOWBALL', 'fthrow'): {
            'damage': 2.4,
            'function_name': 'game_shootthrowf',
            'fallback_path': 'mewtwo_shadowball',
            'fallback_file': 'ShootThrowF.txt'
        },
        
        ('fox', 'FIGHTER_FOX_GENERATE_ARTICLE_BLASTER_BULLET', 'bthrow'): {
            'damage': 2.0,
            'function_name': 'game_flythrowb',
            'fallback_path': 'fox_blaster_bullet',
            'fallback_file': 'FlyThrowB.txt'
        },
        
        ('fox', 'FIGHTER_FOX_GENERATE_ARTICLE_BLASTER_BULLET', 'uthrow'): {
            'damage': 2.0,
            'function_name': 'game_flythrowhi',
            'fallback_path': 'fox_blaster_bullet',
            'fallback_file': 'FlyThrowHi.txt'
        },
        
        ('fox', 'FIGHTER_FOX_GENERATE_ARTICLE_BLASTER_BULLET', 'dthrow'): {
            'damage': 2.0,
            'function_name': 'game_flythrowlw',
            'fallback_path': 'fox_blaster_bullet',
            'fallback_file': 'FlyThrowLw.txt'
        },
        
        ('falco', 'FIGHTER_FOX_GENERATE_ARTICLE_BLASTER_BULLET', 'uthrow'): {
            'damage': 4.0,
            'function_name': 'game_flythrowhi',
            'fallback_path': 'falco_blaster_bullet',
            'fallback_file': 'FlyThrowHi.txt'
        },
        
        ('falco', 'FIGHTER_FOX_GENERATE_ARTICLE_BLASTER_BULLET', 'bthrow'): {
            'damage': 3.0,
            'function_name': 'game_flythrowb',
            'fallback_path': 'falco_blaster_bullet',
            'fallback_file': 'FlyThrowB.txt'
        },
        
        ('falco', 'FIGHTER_FOX_GENERATE_ARTICLE_BLASTER_BULLET', 'dthrow'): {
            'damage': 2.0,
            'function_name': 'game_flythrowlw',
            'fallback_path': 'falco_blaster_bullet',
            'fallback_file': 'FlyThrowLw.txt'
        },
        
        ('pzenigame', 'FIGHTER_PZENIGAME_GENERATE_ARTICLE_WATER', 'fthrow'): {
            'damage': 4.0,
            'function_name': 'game_clash',
            'fallback_path': 'water',
            'fallback_file': 'acmd.rs'
        },
        
        ('demon', 'FIGHTER_DEMON_GENERATE_ARTICLE_BLASTER', 'uthrow'): {
            'damage': 12.0,
            'function_name': 'game_flythrow',
            'fallback_path': 'blaster',
            'fallback_file': 'acmd.rs'
        },
        
        ('pfushigisou', 'FIGHTER_PFUSHIGISOU_GENERATE_ARTICLE_SEED', 'uthrow'): {
            'damage': 7.0,
            'function_name': 'game_clash',
            'fallback_path': 'seed',
            'fallback_file': 'acmd.rs'
        },
    }
    
    article_pattern = r'ArticleModule::generate_article\s*\(\s*boma\s*,\s*\*([^,]+)'
    article_match = re.search(article_pattern, line)
    
    if not article_match:
        return None
    
    article_type = article_match.group(1).strip()
    
    article_key = (character_internal_name, article_type, move_type)
    if article_key not in article_damage_mapping:
        return None
    
    article_info = article_damage_mapping[article_key]
    
    dynamic_damage = read_article_damage_from_script(character_internal_name, article_info)
    if dynamic_damage is not None:
        damage = dynamic_damage
    else:
        damage = article_info['damage']
    
    return damage

def read_article_damage_from_script(character_internal_name, article_info):
    """Attempt to read article damage from the actual script file"""
    fallback_base_path = r"C:\Users\Alex\Documents\GitHub\Roy\SSBU-Dumped-Scripts\smashline-hdr"
    
    possible_paths = [
        os.path.join(fallback_base_path, f"lua2cpp_{character_internal_name}", article_info['fallback_path']),
        os.path.join(fallback_base_path, f"lua2cpp_{character_internal_name}", character_internal_name, article_info['fallback_path']),
        os.path.join(fallback_base_path, article_info['fallback_path']),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            script_file_path = os.path.join(path, article_info['fallback_file'])
            
            if os.path.exists(script_file_path):
                try:
                    with open(script_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                    
                    result = analyze_function(content, article_info['function_name'], 'special', character_internal_name, None)
                    
                    if result and result[0] is not None:
                        return result[0]
                        
                except Exception as e:
                    print(f"Error reading article script {script_file_path}: {e}")
    
    return None
    
def extract_attack_abs_throw_damage(line, variable_values):
    """Extract damage from ATTACK_ABS line with FIGHTER_ATTACK_ABSOLUTE_KIND_THROW only (excludes CATCH/pummel)"""
    pattern = r'ATTACK_ABS\s*\(\s*agent\s*,\s*\*FIGHTER_ATTACK_ABSOLUTE_KIND_THROW\s*,\s*[^,]+\s*,\s*([^,]+)'
    match = re.search(pattern, line)
    if match:
        damage_param = match.group(1).strip()
        return get_numerical_value(damage_param, variable_values)
    
    return None

def extract_throw_attack_damage(line, variable_values, character_internal_name):
    """Extract damage from ATTACK line for throw calculation"""
    attack_pattern = r'ATTACK\s*\(\s*agent\s*,\s*(.*)\)'
    match = re.search(attack_pattern, line)
    if match:
        params_raw = match.group(1)
        params = []
        balance = 0
        current_param = ""
        
        for char in params_raw:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
            
            if char == ',' and balance == 0:
                params.append(current_param.strip())
                current_param = ""
            else:
                current_param += char
        
        if current_param:
            params.append(current_param.strip())
        
        if len(params) >= 4:
            damage_param = params[3].strip()
            if character_internal_name == 'pikmin':
                red_pikmin = {'dmg': 1.05, 'angle': 0}
                return get_numerical_value_enhanced(damage_param, variable_values, red_pikmin)
            else:
                return get_numerical_value(damage_param, variable_values)
    return None

def extract_olimar_base_damage(content, function_name, move_type):
    """Extract base damage values from Olimar's smash attack functions"""
    function_pattern = rf'unsafe extern "C" fn {re.escape(function_name)}\s*\(\s*agent\s*:\s*&mut\s+L2CAgentBase\s*\)\s*\{{'
    function_match = re.search(function_pattern, content)
    
    if not function_match:
        return {}
    
    function_start = function_match.start()
    brace_start = content.find('{', function_start) + 1
    remaining_content = content[brace_start:]
    
    brace_count = 1
    function_end = 0
    
    for i, char in enumerate(remaining_content):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                function_end = i
                break
    
    if function_end == 0:
        return {}
    
    function_body = remaining_content[:function_end]
    
    damage_values = {}
    
    dmg_patterns = re.findall(r'let\s+dmg\s*=\s*([\d.]+)\s*;', function_body)
    
    if dmg_patterns:
        if move_type == 'fsmash':
            if len(dmg_patterns) >= 3:
                damage_values = {
                    'initial': float(dmg_patterns[0]),
                    'mid': float(dmg_patterns[1]),
                    'late': float(dmg_patterns[2])
                }
            else:
                damage_values = {'base': float(dmg_patterns[0])}
        else:
            damage_values = {'base': float(dmg_patterns[0])}
    
    return damage_values
    
def extract_olimar_throw_base_damage(content, function_name, move_type):
    """Extract base damage values from Olimar's throw functions"""
    function_pattern = rf'unsafe extern "C" fn {re.escape(function_name)}\s*\(\s*agent\s*:\s*&mut\s+L2CAgentBase\s*\)\s*\{{'
    function_match = re.search(function_pattern, content)
    
    if not function_match:
        return {}
    
    function_start = function_match.start()
    brace_start = content.find('{', function_start) + 1
    remaining_content = content[brace_start:]
    
    brace_count = 1
    function_end = 0
    
    for i, char in enumerate(remaining_content):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                function_end = i
                break
    
    if function_end == 0:
        return {}
    
    function_body = remaining_content[:function_end]
    
    damage_values = {}
    
    dmg_pattern = r'let\s+dmg\s*=\s*if\s+variation\s*==\s*2\s*\{\s*([\d.]+)\s*\}\s*else\s*\{\s*([\d.]+)\s*\}'
    dmg_match = re.search(dmg_pattern, function_body)
    
    if dmg_match:
        blue_damage = float(dmg_match.group(1))
        other_damage = float(dmg_match.group(2))
        
        damage_values = {
            'blue': blue_damage,
            'other': other_damage
        }
    
    return damage_values

def parse_pikmin_info(folder_path):
    """Parse PikminInfo data from Olimar's mod.rs file"""
    mod_file_path = os.path.join(folder_path, "src", "pikmin", "mod.rs")
    
    pikmin_data = {}
    
    if os.path.exists(mod_file_path):
        try:
            with open(mod_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            patterns = [
                (0, r'0\s*=>\s*PikminInfo\s*\{[^}]*?dmg:\s*([\d.]+)[^}]*?\}'),
                (1, r'1\s*=>\s*PikminInfo\s*\{[^}]*?dmg:\s*([\d.]+)[^}]*?\}'),
                (2, r'2\s*=>\s*PikminInfo\s*\{[^}]*?dmg:\s*([\d.]+)[^}]*?\}'),
                (3, r'3\s*=>\s*PikminInfo\s*\{[^}]*?dmg:\s*([\d.]+)[^}]*?\}'),
                (4, r'_\s*=>\s*PikminInfo\s*\{[^}]*?dmg:\s*([\d.]+)[^}]*?\}'),
            ]
            
            pikmin_names = ['Red', 'Yellow', 'Blue', 'White', 'Purple']
            
            for i, (pikmin_id, pattern) in enumerate(patterns):
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    dmg_mult = float(match.group(1))
                    
                    angle_pattern = pattern.replace(r'dmg:\s*([\d.]+)', r'dmg:\s*[\d.]+[^}]*?angle:\s*(\d+)')
                    angle_match = re.search(angle_pattern, content, re.DOTALL)
                    angle_mod = int(angle_match.group(1)) if angle_match else 0
                    
                    pikmin_data[pikmin_id] = {
                        'name': pikmin_names[i],
                        'dmg': dmg_mult,
                        'angle': angle_mod
                    }
        
        except Exception as e:
            print(f"Error reading Pikmin mod.rs file: {e}")
    
    if not pikmin_data:
        pikmin_data = {
            0: {'name': 'Red', 'dmg': 1.05, 'angle': 0},
            1: {'name': 'Yellow', 'dmg': 0.94, 'angle': 8},
            2: {'name': 'Blue', 'dmg': 1.0, 'angle': 0},
            3: {'name': 'White', 'dmg': 0.75, 'angle': 0},
            4: {'name': 'Purple', 'dmg': 1.2, 'angle': 0}
        }
    
    return pikmin_data

def extract_olimar_smash_frame_from_fallback(fallback_base_path, internal_name, move_type, function_name):
    """Extract frame data for Olimar's smash attacks"""
    
    possible_paths = [
        os.path.join(fallback_base_path, f"lua2cpp_{internal_name}", internal_name),
        os.path.join(fallback_base_path, f"lua2cpp_{internal_name}"),
        os.path.join(fallback_base_path, internal_name),
        os.path.join(fallback_base_path, f"{internal_name}_lua2cpp"),
    ]
    
    fallback_file_mapping = {
        'fsmash': 'AttackS4.txt',
        'usmash': 'AttackHi4.txt',
        'dsmash': 'AttackLw4.txt'
    }
    
    fallback_filename = fallback_file_mapping.get(move_type)
    if not fallback_filename:
        return None
    
    for path in possible_paths:
        if os.path.exists(path):
            fallback_file_path = os.path.join(path, fallback_filename)
            
            if os.path.exists(fallback_file_path):
                try:
                    with open(fallback_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                    
                    function_pattern = rf'{re.escape(function_name)}\s*\('
                    function_match = re.search(function_pattern, content)
                    
                    if not function_match:
                        continue
                    
                    function_start = function_match.start()
                    brace_start = content.find('{', function_start)
                    if brace_start == -1:
                        continue
                    
                    remaining_content = content[brace_start + 1:]
                    brace_count = 1
                    function_end = 0
                    
                    for i, char in enumerate(remaining_content):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                function_end = i
                                break
                    
                    if function_end == 0:
                        continue
                    
                    function_body = remaining_content[:function_end]
                    lines = function_body.split('\n')
                    current_frame = 0.0
                    
                    for line in lines:
                        line = line.strip()
                        
                        if 'frame(' in line and 'lua_state' in line:
                            frame_pattern = r'frame\s*\(\s*lua_state\s*,\s*([0-9.]+)\s*\)'
                            match = re.search(frame_pattern, line)
                            if match:
                                current_frame = float(match.group(1))
                        
                        if 'WorkModule::on_flag' in line and '*FIGHTER_PIKMIN_STATUS_SMASH_ATTACK_FLAG_SHOOT_PIKMIN' in line:
                            return current_frame
                            
                except Exception as e:
                    print(f"Error reading Olimar smash fallback file {fallback_file_path}: {e}")
    
    return None

def extract_megaman_uair_frame(content):
    """Extract frame data for Mega Man's uair"""
    function_pattern = r'unsafe extern "C" fn game_attackairhi\s*\(\s*agent\s*:\s*&mut\s+L2CAgentBase\s*\)\s*\{'
    function_match = re.search(function_pattern, content)
    
    if not function_match:
        return None
    
    function_start = function_match.start()
    brace_start = content.find('{', function_start) + 1
    remaining_content = content[brace_start:]
    
    brace_count = 1
    function_end = 0
    
    for i, char in enumerate(remaining_content):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                function_end = i
                break
    
    if function_end == 0:
        return None
    
    function_body = remaining_content[:function_end]
    lines = function_body.split('\n')
    
    current_animation_frame_marker = 0.0
    motion_events = []
    
    for line in lines:
        line = line.strip()
        
        if 'frame(' in line and ('lua_state' in line or 'agent.lua_state_agent' in line):
            frame_pattern = r'frame\s*\(\s*(?:lua_state|agent\.lua_state_agent)\s*,\s*([0-9.]+)\s*\)'
            match = re.search(frame_pattern, line)
            if match:
                current_animation_frame_marker = float(match.group(1))
        
        if 'FT_MOTION_RATE' in line and 'agent' in line:
            if '10.0/(9.0 - 1.0)' in line:
                motion_events.append((current_animation_frame_marker, 1.25))
            elif 'FT_MOTION_RATE(agent, 1.0)' in line:
                motion_events.append((current_animation_frame_marker, 1.0))
        
        if 'ArticleModule::generate_article' in line and '*FIGHTER_ROCKMAN_GENERATE_ARTICLE_AIRSHOOTER' in line:
            article_frame = current_animation_frame_marker
            
            real_frame = 0.0
            last_frame = 0.0
            current_rate = 1.0
            
            for event_frame, rate in motion_events:
                if event_frame <= article_frame:
                    time_segment = event_frame - last_frame
                    if time_segment > 0:
                        real_frame += time_segment / current_rate
                    last_frame = event_frame
                    current_rate = rate
            
            remaining_time = article_frame - last_frame
            if remaining_time > 0:
                real_frame += remaining_time / current_rate
            
            if motion_events:
                real_frame += 1.0
                
            return real_frame
    
    return None

def extract_miigunner_fair_frame(content):
    """Extract frame data for Mii Gunner's fair"""
    function_pattern = r'unsafe extern "C" fn game_attackairf\s*\(\s*agent\s*:\s*&mut\s+L2CAgentBase\s*\)\s*\{'
    function_match = re.search(function_pattern, content)
    
    if not function_match:
        return None
    
    function_start = function_match.start()
    brace_start = content.find('{', function_start) + 1
    remaining_content = content[brace_start:]
    
    brace_count = 1
    function_end = 0
    
    for i, char in enumerate(remaining_content):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                function_end = i
                break
    
    if function_end == 0:
        return None
    
    function_body = remaining_content[:function_end]
    lines = function_body.split('\n')
    
    current_animation_frame_marker = 0.0
    
    for line in lines:
        line = line.strip()
        
        if 'frame(' in line and ('lua_state' in line or 'agent.lua_state_agent' in line):
            frame_pattern = r'frame\s*\(\s*(?:lua_state|agent\.lua_state_agent)\s*,\s*([0-9.]+)\s*\)'
            match = re.search(frame_pattern, line)
            if match:
                current_animation_frame_marker = float(match.group(1))
        
        if 'ArticleModule::generate_article' in line and '*FIGHTER_MIIGUNNER_GENERATE_ARTICLE_ATTACKAIRF_BULLET' in line:
            return current_animation_frame_marker
    
    return None

def extract_steve_dtilt_frame(content):
    """Extract frame data for Steve's dtilt"""
    function_start_text = 'unsafe extern "C" fn game_attacklw3(agent: &mut L2CAgentBase) {'
    function_start = content.find(function_start_text)
    
    if function_start == -1:
        return None
    
    brace_start = content.find('{', function_start) + 1
    remaining_content = content[brace_start:]
    
    brace_count = 1
    function_end = 0
    
    for i, char in enumerate(remaining_content):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                function_end = i
                break
    
    if function_end == 0:
        return None
    
    function_body = remaining_content[:function_end]
    lines = function_body.split('\n')
    
    current_animation_frame_marker = 0.0
    
    for line in lines:
        line = line.strip()
        
        if 'frame(' in line and ('lua_state' in line or 'agent.lua_state_agent' in line):
            frame_pattern = r'frame\s*\(\s*(?:lua_state|agent\.lua_state_agent)\s*,\s*([0-9.]+)\s*\)'
            match = re.search(frame_pattern, line)
            if match:
                current_animation_frame_marker = float(match.group(1))
        
        if 'ArticleModule::generate_article' in line and '*FIGHTER_PICKEL_GENERATE_ARTICLE_FIRE' in line:
            return current_animation_frame_marker
    
    return None

def parse_motion_rate_changes(line, variable_values):
    """Parse FT_MOTION_RATE_RANGE, MotionModule::set_rate, FT_DESIRED_RATE and FT_MOTION_RATE lines"""
    range_pattern = r'FT_MOTION_RATE_RANGE\s*\(\s*agent\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)'
    match_range = re.search(range_pattern, line)
    
    if match_range:
        start_orig_raw = match_range.group(1).strip()
        end_orig_raw = match_range.group(2).strip()
        new_duration_raw = match_range.group(3).strip()

        start_orig = get_numerical_value(start_orig_raw, variable_values)
        end_orig = get_numerical_value(end_orig_raw, variable_values)
        new_duration = get_numerical_value(new_duration_raw, variable_values)

        if start_orig is None or end_orig is None or new_duration is None:
            return None
        
        original_segment_duration = end_orig - start_orig
        if original_segment_duration <= 0:
            return None 
            
        return {
            'type': 'range',
            'start_orig': start_orig,
            'end_orig': end_orig,
            'new_duration': new_duration,
            'scale_factor': new_duration / original_segment_duration,
        }
    
    desired_rate_pattern = r'FT_DESIRED_RATE\s*\(\s*agent\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)'
    match_desired = re.search(desired_rate_pattern, line)
    
    if match_desired:
        original_frames_raw = match_desired.group(1).strip()
        desired_frames_raw = match_desired.group(2).strip()

        original_frames = get_numerical_value(original_frames_raw, variable_values)
        desired_frames = get_numerical_value(desired_frames_raw, variable_values)

        if original_frames is None or desired_frames is None:
            return None
        
        if original_frames <= 0:
            return None
            
        return {
            'type': 'desired_rate',
            'original_frames': original_frames,
            'desired_frames': desired_frames,
            'scale_factor': desired_frames / original_frames,
        }
    
    motion_module_set_rate_pattern = r'MotionModule::set_rate\s*\(\s*boma\s*,\s*(.*)\);?'
    ft_motion_rate_pattern = r'FT_MOTION_RATE\s*\(\s*agent\s*,\s*(.*)\);?'

    match_motion_module_set_rate = re.search(motion_module_set_rate_pattern, line)
    match_ft_motion_rate = re.search(ft_motion_rate_pattern, line)

    raw_args_string_full = None
    function_type = None

    if match_motion_module_set_rate:
        raw_args_string_full = match_motion_module_set_rate.group(1).strip()
        function_type = 'MotionModule::set_rate'
    elif match_ft_motion_rate:
        raw_args_string_full = match_ft_motion_rate.group(1).strip()
        function_type = 'FT_MOTION_RATE'

    if raw_args_string_full:
        if raw_args_string_full.endswith(')'):
            raw_args_string_full = raw_args_string_full[:-1].strip()

        params = []
        balance = 0
        current_param = ""
        
        for char in raw_args_string_full:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
            
            if char == ',' and balance == 0:
                params.append(current_param.strip())
                current_param = ""
            else:
                current_param += char
        
        if current_param:
            params.append(current_param.strip())
        
        if len(params) >= 1:
            rate_expression = params[-1]

            open_parens = rate_expression.count('(')
            close_parens = rate_expression.count(')')
            if open_parens > close_parens:
                rate_expression += ')' * (open_parens - close_parens)

            rate_value = get_numerical_value(rate_expression, variable_values)
            
            if rate_value is not None:
                return {
                    'type': function_type,
                    'rate_value': rate_value
                }
    
    return None

def calculate_real_frame_with_motion_module(animation_original_frame, frame_events):
    """
    Calculate real frame considering FT_MOTION_RATE_RANGE, MotionModule::set_rate, and FT_DESIRED_RATE calls.
    
    A 'rate' or 'scale_factor' from these functions is a duration multiplier.
    A value of 0.5 means the animation segment plays in half the time (2x speed).
    The calculation uses a speed_multiplier (current_rate), which is 1.0 / duration_multiplier.
    real_frames = animation_frames / speed_multiplier
    """

    if not frame_events:
        return animation_original_frame
    
    real_frame = 0.0
    current_original_frame = 0.0
    current_speed_multiplier = 1.0
    final_frame_offset = 0.0

    has_initial_motion_rate_change = False
    for event_frame, motion_data in frame_events:
        if event_frame <= 0.0:
            if (motion_data['type'] == 'MotionModule::set_rate' and motion_data['rate_value'] != 1.0) or \
               (motion_data['type'] == 'FT_MOTION_RATE' and motion_data['rate_value'] != 1.0) or \
               (motion_data['type'] == 'range' and motion_data['scale_factor'] != 1.0) or \
               (motion_data['type'] == 'desired_rate' and motion_data['scale_factor'] != 1.0):
                has_initial_motion_rate_change = True
                break
    
    if has_initial_motion_rate_change:
        final_frame_offset = 1.0
            
    sorted_events = sorted(frame_events, key=lambda x: x[0])
    
    desired_rate_segments = []
    for event_frame, motion_data in sorted_events:
        if motion_data['type'] == 'desired_rate':
            desired_rate_segments.append({
                'start': event_frame,
                'end': event_frame + motion_data['original_frames'],
                'scale_factor': motion_data['scale_factor']
            })
    
    debug_snake = animation_original_frame == 17.0 and any('snake' in str(event) for event in frame_events)
    
    if desired_rate_segments:
        desired_rate_segments.sort(key=lambda x: x['start'])
        
        cumulative_real_time = 0.0
        last_segment_end = 0.0
        
        for segment in desired_rate_segments:
            if segment['start'] > last_segment_end:
                normal_rate_duration = segment['start'] - last_segment_end
                
                if animation_original_frame <= segment['start']:
                    remaining_frames = animation_original_frame - last_segment_end
                    result = cumulative_real_time + remaining_frames + final_frame_offset
                    return result
                cumulative_real_time += normal_rate_duration
            
            segment_duration = segment['end'] - segment['start']
            
            if animation_original_frame <= segment['end']:
                frames_into_segment = animation_original_frame - segment['start']
                real_time_in_segment = frames_into_segment * segment['scale_factor']
                result = cumulative_real_time + real_time_in_segment + final_frame_offset
                return result
            else:
                real_segment_duration = segment_duration * segment['scale_factor']
                cumulative_real_time += real_segment_duration
                last_segment_end = segment['end']
        
        if animation_original_frame > last_segment_end:
            remaining_time = animation_original_frame - last_segment_end
            cumulative_real_time += remaining_time * 1.0
        
        result = cumulative_real_time + final_frame_offset
        return result
    
    for event_frame, motion_data in sorted_events:
        if motion_data['type'] == 'desired_rate':
            continue
            
        time_segment = event_frame - current_original_frame
        if time_segment > 0:
            segment_real_time = time_segment / current_speed_multiplier
            real_frame += segment_real_time
      
        current_original_frame = event_frame
        
        if event_frame == animation_original_frame:
            return real_frame + final_frame_offset
        
        if event_frame > animation_original_frame:
            real_frame -= (time_segment / current_speed_multiplier) 
            
            segment_duration_up_to_target = animation_original_frame - (event_frame - time_segment)
            real_frame += segment_duration_up_to_target / current_speed_multiplier
            return real_frame + final_frame_offset
        
        if motion_data['type'] == 'MotionModule::set_rate':
            current_speed_multiplier = motion_data['rate_value']
            if current_speed_multiplier <= 0:
                current_speed_multiplier = 1.0
        elif motion_data['type'] == 'FT_MOTION_RATE':
            duration_multiplier = motion_data['rate_value']
            if duration_multiplier is not None and duration_multiplier > 0:
                current_speed_multiplier = 1.0 / duration_multiplier
            else:
                current_speed_multiplier = 1.0
        elif motion_data['type'] == 'range':
            duration_multiplier = motion_data['scale_factor']
            if duration_multiplier is not None and duration_multiplier > 0:
                current_speed_multiplier = 1.0 / duration_multiplier
            else:
                current_speed_multiplier = 1.0

    if animation_original_frame > current_original_frame:
        remaining_original_time = animation_original_frame - current_original_frame
        real_frame += remaining_original_time / current_speed_multiplier
    
    return real_frame + final_frame_offset

def parse_motion_list_yml(file_path):
    """Parse motion_list.yml to extract game_script mappings, animation names, and cancel_frames"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        motion_data = {}
        
        if not data:
            return motion_data
        
        if 'list' in data:
            source_data = data['list']
        else:
            source_data = data
            
        for motion_key, motion_info in source_data.items():
            if isinstance(motion_info, dict):
                game_script = motion_info.get('game_script', '')
                
                extra = motion_info.get('extra')
                cancel_frame = None
                if extra and isinstance(extra, dict):
                    if 'cancel_frame' in extra:
                        cancel_frame = extra['cancel_frame']
                
                animations = motion_info.get('animations', [])
                animation_name = ''
                if animations and len(animations) > 0 and isinstance(animations[0], dict):
                    animation_name = animations[0].get('name', '')
                
                motion_data[motion_key] = {
                    'game_script': game_script,
                    'animation_name': animation_name,
                    'cancel_frame': cancel_frame
                }
        
        return motion_data
        
    except Exception as e:
        print(f"Error parsing motion file at {file_path}: {e}")
        return {}

def get_animation_final_frame(animation_json_path):
    """Get final_frame_index from animation JSON file"""
    try:
        with open(animation_json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        final_frame_index = data.get('final_frame_index')
        if final_frame_index is not None:
            return int(final_frame_index)
        
        if 'animation' in data:
            final_frame_index = data['animation'].get('final_frame_index')
            if final_frame_index is not None:
                return int(final_frame_index)
        
        return None
        
    except Exception as e:
        print(f"Error reading animation JSON at {animation_json_path}: {e}")
        return None

def create_game_script_to_move_mapping():
    """Create mapping from game_script names to move types"""
    move_to_script = {
        'jab1': 'game_attack11',
        'jab2': 'game_attack12', 
        'jab3': 'game_attack13',
        'ftilt': 'game_attacks3',
        'utilt': 'game_attackhi3',
        'dtilt': 'game_attacklw3',
        'fsmash': 'game_attacks4',
        'usmash': 'game_attackhi4',
        'dsmash': 'game_attacklw4',
        'nair': 'game_attackairn',
        'fair': 'game_attackairf',
        'bair': 'game_attackairb',
        'uair': 'game_attackairhi',
        'dair': 'game_attackairlw',
        'dash_attack': 'game_attackdash',
        'grab': 'game_catch',
        'dash_grab': 'game_catchdash',
        'pivot_grab': 'game_catchturn',
        'pummel': 'game_catchattack',
        'fthrow': 'game_throwf',
        'bthrow': 'game_throwb',
        'uthrow': 'game_throwhi',
        'dthrow': 'game_throwlw',
        'neutral_b': 'game_specialn',
        'side_b': 'game_specials',
        'up_b': 'game_specialhi',
        'down_b': 'game_speciallw',
        'neutral_b_air': 'game_specialairn',
        'side_b_air': 'game_specialairs',
        'up_b_air': 'game_specialairhi',
        'down_b_air': 'game_specialairlw',
    }
    
    script_to_move = {}
    for move_type, script_name in move_to_script.items():
        script_to_move[script_name] = move_type
    
    script_to_move['game_attack11melee'] = 'jab1'
    script_to_move['game_attacks3melee'] = 'ftilt'
    script_to_move['game_attackairnmelee'] = 'nair'
    script_to_move['game_attack100'] = 'jab1'
    script_to_move['game_catchattack_nana'] = 'pummel'
    script_to_move['game_specialsfailed'] = 'dash_attack'
    
    script_to_move['game_attack11w'] = 'jab1'
    script_to_move['game_attack11s'] = 'jab1'
    script_to_move['game_attack12s'] = 'jab2'
    script_to_move['game_attacks3w'] = 'ftilt'
    script_to_move['game_attacks3s'] = 'ftilt'
    script_to_move['game_attackhi3w'] = 'utilt'
    script_to_move['game_attackhi3s'] = 'utilt'
    script_to_move['game_attacklw3w'] = 'dtilt'
    script_to_move['game_attacklw3s'] = 'dtilt'
    
    script_to_move['game_attacks4s2'] = 'fsmash'
    script_to_move['game_attacks4s3'] = 'fsmash'
    script_to_move['game_attacks4sjump'] = 'fsmash'
    
    script_to_move['game_throwff'] = 'fthrow'
    script_to_move['game_throwfb'] = 'fthrow'
    script_to_move['game_throwfhi'] = 'fthrow'
    script_to_move['game_throwflw'] = 'fthrow'
    
    return script_to_move

    """Get FAF data from animation JSON files as fallback"""
    animation_faf_data = {}
    
    animation_file_mapping = {
        'jab1': 'c00attack11.json',
        'jab2': 'c00attack12.json', 
        'jab3': 'c00attack13.json',
        'ftilt': 'c00attacks3s.json',
        'utilt': 'c00attackhi3.json',
        'dtilt': 'c00attacklw3.json',
        'fsmash': 'c00attacks4s.json',
        'usmash': 'c00attackhi4.json',
        'dsmash': 'c00attacklw4.json',
        'nair': 'c00attackairn.json',
        'fair': 'c00attackairf.json',
        'bair': 'c00attackairb.json',
        'uair': 'c00attackairhi.json',
        'dair': 'c00attackairlw.json',
        'dash_attack': 'c00attackdash.json',
    }
    
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    
    if not os.path.exists(character_animations_path):
        return animation_faf_data
    
    for move_type, filename in animation_file_mapping.items():
        possible_files = [
            filename,
            filename.replace('c00', 'c01'),
            filename.replace('c00', 'c02'),
            filename.replace('c00', 'c03'),
            filename.replace('c00', 'c04'),
            filename.replace('c00', 'c05'),
            filename.replace('c00', 'c06'),
            filename.replace('c00', 'c07'),
            filename.replace('c00', 'c08'),
            filename.replace('c00', 'c09'),
        ]
        
        for possible_file in possible_files:
            animation_json_path = os.path.join(character_animations_path, possible_file)
            
            if os.path.exists(animation_json_path):
                final_frame = get_animation_final_frame(animation_json_path)
                if final_frame is not None:
                    animation_faf_data[move_type] = int(final_frame)
                    break
    
    return animation_faf_data
    """Get FAF data from animation JSON files as fallback"""
    animation_faf_data = {}
    
    animation_file_mapping = {
        'jab1': 'c00attack11.json',
        'jab2': 'c00attack12.json', 
        'jab3': 'c00attack13.json',
        'ftilt': 'c00attacks3s.json',
        'utilt': 'c00attackhi3.json',
        'dtilt': 'c00attacklw3.json',
        'fsmash': 'c00attacks4s.json',
        'usmash': 'c00attackhi4.json',
        'dsmash': 'c00attacklw4.json',
        'nair': 'c00attackairn.json',
        'fair': 'c00attackairf.json',
        'bair': 'c00attackairb.json',
        'uair': 'c00attackairhi.json',
        'dair': 'c00attackairlw.json',
        'dash_attack': 'c00attackdash.json',
    }
    
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    
    if not os.path.exists(character_animations_path):
        return animation_faf_data
    
    for move_type, filename in animation_file_mapping.items():
        possible_files = [
            filename,
            filename.replace('c00', 'c01'),
            filename.replace('c00', 'c02'),
            filename.replace('c00', 'c03'),
            filename.replace('c00', 'c04'),
            filename.replace('c00', 'c05'),
            filename.replace('c00', 'c06'),
            filename.replace('c00', 'c07'),
            filename.replace('c00', 'c08'),
            filename.replace('c00', 'c09'),
        ]
        
        for possible_file in possible_files:
            animation_json_path = os.path.join(character_animations_path, possible_file)
            
            if os.path.exists(animation_json_path):
                final_frame = get_animation_final_frame(animation_json_path)
                if final_frame is not None:
                    animation_faf_data[move_type] = int(final_frame)
                    break
    
    return animation_faf_data
    """Get FAF data from animation JSON files as fallback"""
    animation_faf_data = {}
    
    animation_file_mapping = {
        'jab1': 'c00attack11.json',
        'jab2': 'c00attack12.json', 
        'jab3': 'c00attack13.json',
        'ftilt': 'c00attacks3s.json',
        'utilt': 'c00attackhi3.json',
        'dtilt': 'c00attacklw3.json',
        'fsmash': 'c00attacks4s.json',
        'usmash': 'c00attackhi4.json',
        'dsmash': 'c00attacklw4.json',
        'nair': 'c00attackairn.json',
        'fair': 'c00attackairf.json',
        'bair': 'c00attackairb.json',
        'uair': 'c00attackairhi.json',
        'dair': 'c00attackairlw.json',
        'dash_attack': 'c00attackdash.json',
    }
    
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    
    if not os.path.exists(character_animations_path):
        return animation_faf_data
    
    for move_type, filename in animation_file_mapping.items():
        possible_files = [
            filename,
            filename.replace('c00', 'c01'),
            filename.replace('c00', 'c02'),
            filename.replace('c00', 'c03'),
            filename.replace('c00', 'c04'),
            filename.replace('c00', 'c05'),
            filename.replace('c00', 'c06'),
            filename.replace('c00', 'c07'),
            filename.replace('c00', 'c08'),
            filename.replace('c00', 'c09'),
        ]
        
        for possible_file in possible_files:
            animation_json_path = os.path.join(character_animations_path, possible_file)
            
            if os.path.exists(animation_json_path):
                final_frame = get_animation_final_frame(animation_json_path)
                if final_frame is not None:
                    animation_faf_data[move_type] = int(final_frame)
                    break
    
    return animation_faf_data
    """Get FAF data from animation JSON files as fallback"""
    animation_faf_data = {}
    
    animation_file_mapping = {
        'jab1': 'c00attack11.json',
        'jab2': 'c00attack12.json', 
        'jab3': 'c00attack13.json',
        'ftilt': 'c00attacks3s.json',
        'utilt': 'c00attackhi3.json',
        'dtilt': 'c00attacklw3.json',
        'fsmash': 'c00attacks4s.json',
        'usmash': 'c00attackhi4.json',
        'dsmash': 'c00attacklw4.json',
        'nair': 'c00attackairn.json',
        'fair': 'c00attackairf.json',
        'bair': 'c00attackairb.json',
        'uair': 'c00attackairhi.json',
        'dair': 'c00attackairlw.json',
        'dash_attack': 'c00attackdash.json',
    }
    
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    
    if not os.path.exists(character_animations_path):
        return animation_faf_data
    
    for move_type, filename in animation_file_mapping.items():
        possible_files = [
            filename,
            filename.replace('c00', 'c01'),
            filename.replace('c00', 'c02'),
            filename.replace('c00', 'c03'),
            filename.replace('c00', 'c04'),
            filename.replace('c00', 'c05'),
            filename.replace('c00', 'c06'),
            filename.replace('c00', 'c07'),
            filename.replace('c00', 'c08'),
            filename.replace('c00', 'c09'),
        ]
        
        for possible_file in possible_files:
            animation_json_path = os.path.join(character_animations_path, possible_file)
            
            if os.path.exists(animation_json_path):
                final_frame = get_animation_final_frame(animation_json_path)
                if final_frame is not None:
                    animation_faf_data[move_type] = int(final_frame)
                    break
    
    return animation_faf_data
    """Get FAF data from animation JSON files as fallback"""
    animation_faf_data = {}
    
    animation_file_mapping = {
        'jab1': 'c00attack11.json',
        'jab2': 'c00attack12.json', 
        'jab3': 'c00attack13.json',
        'ftilt': 'c00attacks3s.json',
        'utilt': 'c00attackhi3.json',
        'dtilt': 'c00attacklw3.json',
        'fsmash': 'c00attacks4s.json',
        'usmash': 'c00attackhi4.json',
        'dsmash': 'c00attacklw4.json',
        'nair': 'c00attackairn.json',
        'fair': 'c00attackairf.json',
        'bair': 'c00attackairb.json',
        'uair': 'c00attackairhi.json',
        'dair': 'c00attackairlw.json',
        'dash_attack': 'c00attackdash.json',
    }
    
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    
    if not os.path.exists(character_animations_path):
        return animation_faf_data
    
    for move_type, filename in animation_file_mapping.items():
        possible_files = [
            filename,
            filename.replace('c00', 'c04'),
            filename.replace('c00', 'c01'),
            filename.replace('c00', 'c02'),
            filename.replace('c00', 'c03'),
        ]
        
        for possible_file in possible_files:
            animation_json_path = os.path.join(character_animations_path, possible_file)
            
            if os.path.exists(animation_json_path):
                final_frame = get_animation_final_frame(animation_json_path)
                if final_frame is not None:
                    animation_faf_data[move_type] = int(final_frame)
                    break
    
    return animation_faf_data

    """Get FAF data from animation JSON files as fallback"""
    animation_faf_data = {}
    
    animation_file_mapping = {
        'jab1': 'c00attack11.json',
        'jab2': 'c00attack12.json', 
        'jab3': 'c00attack13.json',
        'ftilt': 'c00attacks3s.json',
        'utilt': 'c00attackhi3.json',
        'dtilt': 'c00attacklw3.json',
        'fsmash': 'c00attacks4s.json',
        'usmash': 'c00attackhi4.json',
        'dsmash': 'c00attacklw4.json',
        'nair': 'c00attackairn.json',
        'fair': 'c00attackairf.json',
        'bair': 'c00attackairb.json',
        'uair': 'c00attackairhi.json',
        'dair': 'c00attackairlw.json',
        'dash_attack': 'c00attackdash.json',
    }
    
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    
    if not os.path.exists(character_animations_path):
        return animation_faf_data
    
    for move_type, filename in animation_file_mapping.items():
        possible_files = [
            filename,
            filename.replace('c00', 'c01'),
            filename.replace('c00', 'c02'),
            filename.replace('c00', 'c03'),
            filename.replace('c00', 'c04'),
            filename.replace('c00', 'c05'),
            filename.replace('c00', 'c06'),
            filename.replace('c00', 'c07'),
            filename.replace('c00', 'c08'),
            filename.replace('c00', 'c09'),
        ]
        
        for possible_file in possible_files:
            animation_json_path = os.path.join(character_animations_path, possible_file)
            
            if os.path.exists(animation_json_path):
                final_frame = get_animation_final_frame(animation_json_path)
                if final_frame is not None:
                    animation_faf_data[move_type] = int(final_frame)
                    break
    
    return animation_faf_data

    """Get FAF data from animation JSON files as fallback"""
    animation_faf_data = {}
    
    animation_file_mapping = {
        'jab1': 'c00attack11.json',
        'jab2': 'c00attack12.json', 
        'jab3': 'c00attack13.json',
        'ftilt': 'c00attacks3s.json',
        'utilt': 'c00attackhi3.json',
        'dtilt': 'c00attacklw3.json',
        'fsmash': 'c00attacks4s.json',
        'usmash': 'c00attackhi4.json',
        'dsmash': 'c00attacklw4.json',
        'nair': 'c00attackairn.json',
        'fair': 'c00attackairf.json',
        'bair': 'c00attackairb.json',
        'uair': 'c00attackairhi.json',
        'dair': 'c00attackairlw.json',
        'dash_attack': 'c00attackdash.json',
    }
    
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    
    if not os.path.exists(character_animations_path):
        return animation_faf_data
    
    for move_type, filename in animation_file_mapping.items():
        possible_files = [
            filename,
            filename.replace('c00', 'c01'),
            filename.replace('c00', 'c02'),
            filename.replace('c00', 'c03'),
            filename.replace('c00', 'c04'),
            filename.replace('c00', 'c05'),
            filename.replace('c00', 'c06'),
            filename.replace('c00', 'c07'),
            filename.replace('c00', 'c08'),
            filename.replace('c00', 'c09'),
        ]
        
        for possible_file in possible_files:
            animation_json_path = os.path.join(character_animations_path, possible_file)
            
            if os.path.exists(animation_json_path):
                final_frame = get_animation_final_frame(animation_json_path)
                if final_frame is not None:
                    animation_faf_data[move_type] = int(final_frame)
                    break
    
    return animation_faf_data

    """Get FAF data from animation JSON files as fallback"""
    animation_faf_data = {}
    
    animation_file_mapping = {
        'jab1': 'c00attack11.json',
        'jab2': 'c00attack12.json', 
        'jab3': 'c00attack13.json',
        'ftilt': 'c00attacks3s.json',
        'utilt': 'c00attackhi3.json',
        'dtilt': 'c00attacklw3.json',
        'fsmash': 'c00attacks4s.json',
        'usmash': 'c00attackhi4.json',
        'dsmash': 'c00attacklw4.json',
        'nair': 'c00attackairn.json',
        'fair': 'c00attackairf.json',
        'bair': 'c00attackairb.json',
        'uair': 'c00attackairhi.json',
        'dair': 'c00attackairlw.json',
        'dash_attack': 'c00attackdash.json',
    }
    
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    
    if not os.path.exists(character_animations_path):
        return animation_faf_data
    
    for move_type, filename in animation_file_mapping.items():
        possible_files = [
            filename,
            filename.replace('c00', 'c01'),
            filename.replace('c00', 'c02'),
            filename.replace('c00', 'c03'),
            filename.replace('c00', 'c04'),
            filename.replace('c00', 'c05'),
            filename.replace('c00', 'c06'),
            filename.replace('c00', 'c07'),
            filename.replace('c00', 'c08'),
            filename.replace('c00', 'c09'),
        ]
        
        for possible_file in possible_files:
            animation_json_path = os.path.join(character_animations_path, possible_file)
            
            if os.path.exists(animation_json_path):
                final_frame = get_animation_final_frame(animation_json_path)
                if final_frame is not None:
                    animation_faf_data[move_type] = int(final_frame)
                    break
    
    return animation_faf_data

def get_character_faf_data(character_internal_name, animations_base_path, hdr_base_path):
    """FAF data for most attacks"""
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    motion_list_path = os.path.join(character_animations_path, 'motion_list.yml')
    hdr_motion_path = os.path.join(hdr_base_path, 'romfs', 'source', 'fighter', character_internal_name, 'motion', 'body', 'motion_patch.yaml')
    
    motion_data = {}
    
    if os.path.exists(motion_list_path):
        motion_data = parse_motion_list_yml(motion_list_path)
    
    if os.path.exists(hdr_motion_path):
        patch_data = parse_motion_list_yml(hdr_motion_path)
        
        for motion_key, patch_info in patch_data.items():
            if motion_key in motion_data:
                original_info = motion_data[motion_key]
                if patch_info.get('cancel_frame') is not None:
                    original_info['cancel_frame'] = patch_info['cancel_frame']
            else:
                motion_data[motion_key] = patch_info
    
    if not motion_data:
        return {}
    
    motion_key_to_move = {
        'attack_11': 'jab1',
        'attack_12': 'jab2', 
        'attack_13': 'jab3',
        'attack_s3_s': 'ftilt',
        'attack_hi3': 'utilt',
        'attack_lw3': 'dtilt',
        'attack_s4_s': 'fsmash',
        'attack_hi4': 'usmash',
        'attack_lw4': 'dsmash',
        'attack_air_n': 'nair',
        'attack_air_f': 'fair',
        'attack_air_b': 'bair',
        'attack_air_hi': 'uair',
        'attack_air_lw': 'dair',
        'attack_dash': 'dash_attack',
        'catch': 'grab',
        'catch_dash': 'dash_grab',
        'catch_turn': 'pivot_grab',
        'catch_attack': 'pummel',
        'catch_attack_f': 'pummel',
        'catch_attack_s': 'pummel',
        'catch_atk': 'pummel',
        'catch_attack_w': 'pummel',
        'catchattack': 'pummel',
        'throw_f': 'fthrow',
        'throw_b': 'bthrow',
        'throw_hi': 'uthrow',
        'throw_lw': 'dthrow',
        'special_n': 'neutral_b',
        'special_s': 'side_b',
        'special_hi': 'up_b',
        'special_lw': 'down_b',
        'special_air_n': 'neutral_b_air',
        'special_air_s': 'side_b_air',
        'special_air_hi': 'up_b_air',
        'special_air_lw': 'down_b_air',
        
        'attack_11_w': 'jab1',
        'attack_11_s': 'jab1',
        'attack_12_s': 'jab2',
        
        'attack_100_end': 'jab1',
    }
    
    character_faf_data = {}
    
    for motion_key, motion_info in motion_data.items():
        move_type = motion_key_to_move.get(motion_key)
        if not move_type:
            continue
        
        cancel_frame = motion_info.get('cancel_frame', 0)
        
        if cancel_frame and cancel_frame > 0:
            character_faf_data[move_type] = cancel_frame
        elif cancel_frame == 0:
            animation_faf = get_single_move_animation_faf(character_internal_name, animations_base_path, move_type)
            if animation_faf and animation_faf > 0:
                character_faf_data[move_type] = animation_faf
    
    animation_faf_data = get_animation_faf_fallback(character_internal_name, animations_base_path)
    
    for move_type, faf_value in animation_faf_data.items():
        if move_type not in character_faf_data:
            character_faf_data[move_type] = faf_value
    
    return character_faf_data

def get_single_move_animation_faf(character_internal_name, animations_base_path, move_type):
    """Get FAF data from animation JSON file for a specific move"""
    
    animation_file_patterns = {
        'jab1': 'attack11',
        'jab2': 'attack12', 
        'jab3': 'attack13',
        'ftilt': ['attacks3', 'attacks3s', 'attacks3w'],
        'utilt': ['attackhi3', 'attackhi3s', 'attackhi3w'],
        'dtilt': ['attacklw3', 'attacklw3s', 'attacklw3w'],
        'fsmash': 'attacks4',
        'usmash': 'attackhi4',
        'dsmash': 'attacklw4',
        'nair': 'attackairn',
        'fair': 'attackairf',
        'bair': 'attackairb',
        'uair': 'attackairhi',
        'dair': 'attackairlw',
        'dash_attack': 'attackdash',
        'grab': 'catch',
        'dash_grab': 'catchdash',
        'pivot_grab': 'catchturn',
        'pummel': 'catchattack',
        'fthrow': 'throwf',
        'bthrow': 'throwb',
        'uthrow': 'throwhi',
        'dthrow': 'throwlw',
        'neutral_b': 'specialn',
        'side_b': 'specials',
        'up_b': 'specialhi',
        'down_b': 'speciallw',
    }
    
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    
    if not os.path.exists(character_animations_path):
        return None
    
    patterns = animation_file_patterns.get(move_type)
    if not patterns:
        return None
    
    try:
        all_files = os.listdir(character_animations_path)
        json_files = [f for f in all_files if f.endswith('.json')]
        
        if isinstance(patterns, str):
            patterns = [patterns]
        
        matching_files = []
        for pattern in patterns:
            matching_files.extend([f for f in json_files if pattern in f.lower()])
        
        matching_files = list(set(matching_files))
        
        for matching_file in matching_files:
            animation_json_path = os.path.join(character_animations_path, matching_file)
            final_frame = get_animation_final_frame(animation_json_path)
            if final_frame is not None and final_frame > 0:
                return int(final_frame)
                
    except Exception as e:
        print(f"Error reading animation directory for {character_internal_name} {move_type}: {e}")
    
    return None

def get_animation_faf_fallback(character_internal_name, animations_base_path):
    """Get FAF data from animation JSON files as fallback"""
    animation_faf_data = {}
    
    animation_file_mapping = {
        'jab1': 'c00attack11.json',
        'jab2': 'c00attack12.json', 
        'jab3': 'c00attack13.json',
        'ftilt': 'c00attacks3s.json',
        'utilt': 'c00attackhi3.json',
        'dtilt': 'c00attacklw3.json',
        'fsmash': 'c00attacks4s.json',
        'usmash': 'c00attackhi4.json',
        'dsmash': 'c00attacklw4.json',
        'nair': 'c00attackairn.json',
        'fair': 'c00attackairf.json',
        'bair': 'c00attackairb.json',
        'uair': 'c00attackairhi.json',
        'dair': 'c00attackairlw.json',
        'dash_attack': 'c00attackdash.json',
    }
    
    character_animations_path = os.path.join(animations_base_path, character_internal_name, 'body')
    
    if not os.path.exists(character_animations_path):
        return animation_faf_data
    
    for move_type, filename in animation_file_mapping.items():
        possible_files = [
            filename,
            filename.replace('c00', 'c01'),
            filename.replace('c00', 'c02'),
            filename.replace('c00', 'c03'),
            filename.replace('c00', 'c04'),
            filename.replace('c00', 'c05'),
            filename.replace('c00', 'c06'),
            filename.replace('c00', 'c07'),
            filename.replace('c00', 'c08'),
            filename.replace('c00', 'c09'),
        ]
        
        for possible_file in possible_files:
            animation_json_path = os.path.join(character_animations_path, possible_file)
            
            if os.path.exists(animation_json_path):
                final_frame = get_animation_final_frame(animation_json_path)
                if final_frame is not None:
                    animation_faf_data[move_type] = int(final_frame)
                    break
    
    return animation_faf_data

def analyze_function(content, function_name, move_type, character_internal_name, character_faf_data=None):
    """Analyze a specific function and return damage/frame data"""
    
    function_pattern = rf'unsafe extern "C" fn {re.escape(function_name)}\s*\(\s*agent\s*:\s*&mut\s+L2CAgentBase\s*\)\s*\{{'
    function_match = re.search(function_pattern, content)
    
    if function_match:
        function_start = function_match.start()
    else:
        if 'throw' in function_name.lower() or 'catchattack' in function_name.lower():
            alt_function_names = [
                function_name.replace('game_', '').capitalize(),
                function_name.replace('game_', '')
            ]
            found = False
            for alt_name in alt_function_names:
                alt_pattern = rf'unsafe extern "C" fn {re.escape(alt_name)}\s*\(\s*agent\s*:\s*&mut\s+L2CAgentBase\s*\)\s*\{{'
                alt_match = re.search(alt_pattern, content)
                if alt_match:
                    function_start = alt_match.start()
                    found = True
                    break
            if not found:
                return None
        else:
            return None
    
    brace_start = content.find('{', function_start) + 1
    remaining_content = content[brace_start:]
    
    brace_count = 1
    function_end = 0
    
    for i, char in enumerate(remaining_content):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                function_end = i
                break
    
    if function_end == 0:
        return None
    
    function_body = remaining_content[:function_end]
    
    lines = function_body.split('\n')
    
    is_throw_move = move_type in ['pummel', 'fthrow', 'bthrow', 'uthrow', 'dthrow']
    
    frame_events = []
    attack_lines_with_frame = []
    throw_release_frame = None
    current_animation_frame_marker = 0.0
    
    variable_values = {}
    for line in function_body.split('\n'):
        line = line.strip()
        if line.startswith('let ') and '=' in line and ';' in line:
            parts = line.split('=', 1)
            if len(parts) == 2:
                var_name = parts[0].replace('let ', '').strip()
                var_value_raw = parts[1].split(';')[0].strip()
                variable_values[var_name] = var_value_raw
                
    total_throw_damage = None
    if is_throw_move:
        total_throw_damage = calculate_total_throw_damage(function_body, variable_values, character_internal_name, move_type)
    
    is_villager_dash = character_internal_name == 'murabito' and move_type == 'dash_attack'
    is_isabelle_dash = character_internal_name == 'shizue' and move_type == 'dash_attack'
    is_villager_fsmash = character_internal_name == 'murabito' and move_type == 'fsmash'
    
    synthetic_data_added = False
    
    skip_conditional_attacks = False
    conditional_depth = 0
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if character_internal_name == 'brave':
            if 'if VarModule::is_flag(agent.battle_object, vars::brave::instance::PSYCHE_UP_ACTIVE)' in line:
                skip_conditional_attacks = True
                conditional_depth = 1
                i += 1
                continue
            elif skip_conditional_attacks and 'else {' in line:
                skip_conditional_attacks = False
                conditional_depth = 0
                i += 1
                continue
            elif skip_conditional_attacks:
                conditional_depth += line.count('{')
                conditional_depth -= line.count('}')
                if conditional_depth <= 0:
                    skip_conditional_attacks = False
                i += 1
                continue
        
        if 'frame(' in line and ('lua_state' in line or 'agent.lua_state_agent' in line):
            frame_pattern = r'frame\s*\(\s*(?:lua_state|agent\.lua_state_agent)\s*,\s*([0-9.]+)\s*\)'
            match = re.search(frame_pattern, line)
            if match:
                current_animation_frame_marker = float(match.group(1))

        if 'wait(' in line and 'lua_state' in line:
            wait_pattern = r'wait\s*\(\s*lua_state\s*,\s*([0-9.]+)\s*\)'
            match = re.search(wait_pattern, line)
            if match:
                current_animation_frame_marker += float(match.group(1))
                
        if 'for ' in line and ' in 0..' in line:
            loop_match = re.search(r'for\s+\w+\s+in\s+0\.\.(\d+)', line)
            if loop_match:
                loop_iterations = int(loop_match.group(1))
                
                loop_body = []
                brace_count = 1
                j = i + 1
                
                while j < len(lines) and brace_count > 0:
                    loop_line = lines[j]
                    loop_body.append(loop_line)
                    brace_count += loop_line.count('{')
                    brace_count -= loop_line.count('}')
                    j += 1
                
                loop_wait_time = 0.0
                for loop_line in loop_body:
                    loop_line_stripped = loop_line.strip()
                    
                    if 'wait(' in loop_line_stripped and 'lua_state' in loop_line_stripped:
                        wait_match = re.search(r'wait\s*\(\s*lua_state\s*,\s*([0-9.]+)\s*\)', loop_line_stripped)
                        if wait_match:
                            loop_wait_time += float(wait_match.group(1))
                    
                    if 'ATTACK(agent,' in loop_line_stripped and not loop_line_stripped.startswith('//'):
                        attack_lines_with_frame.append((current_animation_frame_marker, loop_line_stripped))
                    
                    if ('CATCH(agent,' in loop_line_stripped) and not loop_line_stripped.startswith('//'):
                        if move_type in ['grab', 'dash_grab', 'pivot_grab']:
                            attack_lines_with_frame.append((current_animation_frame_marker, 'CATCH_GRAB'))
                
                total_loop_wait = loop_wait_time * loop_iterations
                current_animation_frame_marker += total_loop_wait
                
                i = j - 1
                i += 1
                continue

        motion_change = parse_motion_rate_changes(line, variable_values)
        if motion_change:
            frame_events.append((current_animation_frame_marker, motion_change))
        
        if (is_villager_dash or is_isabelle_dash) and 'ArticleModule::shoot' in line:
            if is_villager_dash and ('FIGHTER_MURABITO_GENERATE_ARTICLE_FLOWERPOT' in line or 'FLOWERPOT' in line):
                synthetic_attack = 'ATTACK(agent, 0, 0, Hash40::new("have"), 10.0, 59, 82, 0, 45, 4.2, 0.0, 2.5, 0.0, None, None, None, 1.0, 0.0, *ATTACK_SETOFF_KIND_ON, *ATTACK_LR_CHECK_SPEED, false, 0, 0.0, 0, true, false, false, false, false, *COLLISION_SITUATION_MASK_GA, *COLLISION_CATEGORY_MASK_ALL, *COLLISION_PART_MASK_ALL, false, Hash40::new("collision_attr_normal"), *ATTACK_SOUND_LEVEL_L, *COLLISION_SOUND_ATTR_KICK, *ATTACK_REGION_OBJECT);'
                attack_lines_with_frame.append((current_animation_frame_marker, synthetic_attack))
                synthetic_data_added = True
            elif is_isabelle_dash and ('FIGHTER_SHIZUE_GENERATE_ARTICLE_POT' in line or 'POT' in line):
                synthetic_attack = 'ATTACK(agent, 0, 0, Hash40::new("have"), 10.0, 70, 85, 0, 42, 4.2, 0.0, 2.5, 0.0, None, None, None, 0.6, 0.0, *ATTACK_SETOFF_KIND_ON, *ATTACK_LR_CHECK_F, false, 0, 0.0, 0, true, false, false, false, false, *COLLISION_SITUATION_MASK_GA, *COLLISION_CATEGORY_MASK_ALL, *COLLISION_PART_MASK_ALL, false, Hash40::new("collision_attr_normal"), *ATTACK_SOUND_LEVEL_L, *COLLISION_SOUND_ATTR_KICK, *ATTACK_REGION_OBJECT);'
                attack_lines_with_frame.append((current_animation_frame_marker, synthetic_attack))
                synthetic_data_added = True
        elif is_villager_fsmash and 'ArticleModule::shoot' in line and ('FIGHTER_MURABITO_GENERATE_ARTICLE_BOWLING_BALL' in line or 'BOWLING_BALL' in line):
            pass
        
        if ('ATTACK(agent,' in line or 'ATTACK_ABS(agent,' in line) and not line.strip().startswith('//') and not skip_conditional_attacks:
            attack_lines_with_frame.append((current_animation_frame_marker, line))

        if ('CATCH(agent,' in line) and not line.strip().startswith('//') and not skip_conditional_attacks:
            if move_type in ['grab', 'dash_grab', 'pivot_grab']:
                attack_lines_with_frame.append((current_animation_frame_marker, 'CATCH_GRAB'))

        if character_internal_name == 'rockman' and move_type == 'dair' and 'ArticleModule::generate_article' in line and '*FIGHTER_ROCKMAN_GENERATE_ARTICLE_HARDKNUCKLE' in line:
            throw_release_frame = current_animation_frame_marker
            
        elif character_internal_name == 'pickel' and move_type == 'dsmash' and 'ArticleModule::generate_article' in line and '*FIGHTER_PICKEL_GENERATE_ARTICLE_MELT' in line:
            throw_release_frame = current_animation_frame_marker
        
        elif is_throw_move and 'ATK_HIT_ABS' in line and '*FIGHTER_ATTACK_ABSOLUTE_KIND_THROW' in line:
            throw_release_frame = current_animation_frame_marker
        
        elif is_throw_move and 'ATTACK_ABS' in line and '*FIGHTER_ATTACK_ABSOLUTE_KIND_THROW' in line and throw_release_frame is None:
            if current_animation_frame_marker > 0:
                throw_release_frame = current_animation_frame_marker
        
        if 'if is_excute(agent) {' in line or 'if AttackModule::is_attack(boma) {' in line:
            block_lines = []
            brace_count_block = 1
            j = i + 1
            
            block_start_frame = current_animation_frame_marker
            
            while j < len(lines) and brace_count_block > 0:
                current_line = lines[j]
                block_lines.append(current_line)
                brace_count_block += current_line.count('{')
                brace_count_block -= current_line.count('}')
                j += 1
            
            block_content = '\n'.join(block_lines)
            
            block_current_frame = block_start_frame
            
            block_skip_conditional_attacks = False
            block_conditional_depth = 0
            
            for block_line in block_lines:
                block_line_stripped = block_line.strip()
                
                if character_internal_name == 'brave':
                    if 'if VarModule::is_flag(agent.battle_object, vars::brave::instance::PSYCHE_UP_ACTIVE)' in block_line_stripped:
                        block_skip_conditional_attacks = True
                        block_conditional_depth = 1
                        continue
                    elif block_skip_conditional_attacks and 'else {' in block_line_stripped:
                        block_skip_conditional_attacks = False
                        block_conditional_depth = 0
                        continue
                    elif block_skip_conditional_attacks:
                        block_conditional_depth += block_line_stripped.count('{')
                        block_conditional_depth -= block_line_stripped.count('}')
                        if block_conditional_depth <= 0:
                            block_skip_conditional_attacks = False
                        continue
                
                if 'frame(' in block_line_stripped and ('lua_state' in block_line_stripped or 'agent.lua_state_agent' in block_line_stripped):
                    frame_pattern = r'frame\s*\(\s*(?:lua_state|agent\.lua_state_agent)\s*,\s*([0-9.]+)\s*\)'
                    match = re.search(frame_pattern, block_line_stripped)
                    if match:
                        block_current_frame = float(match.group(1))
                        current_animation_frame_marker = block_current_frame

                if 'wait(' in block_line_stripped and 'lua_state' in block_line_stripped:
                    wait_pattern = r'wait\s*\(\s*lua_state\s*,\s*([0-9.]+)\s*\)'
                    match = re.search(wait_pattern, block_line_stripped)
                    if match:
                        wait_frames = float(match.group(1))
                        block_current_frame += wait_frames
                        current_animation_frame_marker += wait_frames

                motion_change = parse_motion_rate_changes(block_line_stripped, variable_values)
                if motion_change:
                    frame_events.append((block_current_frame, motion_change))

                if (is_villager_dash or is_isabelle_dash) and 'ArticleModule::shoot' in block_line_stripped:
                    if is_villager_dash and 'FIGHTER_MURABITO_GENERATE_ARTICLE_FLOWERPOT' in block_line_stripped:
                        synthetic_attack = 'ATTACK(agent, 0, 0, Hash40::new("have"), 10.0, 59, 82, 0, 45, 4.2, 0.0, 2.5, 0.0, None, None, None, 1.0, 0.0, *ATTACK_SETOFF_KIND_ON, *ATTACK_LR_CHECK_SPEED, false, 0, 0.0, 0, true, false, false, false, false, *COLLISION_SITUATION_MASK_GA, *COLLISION_CATEGORY_MASK_ALL, *COLLISION_PART_MASK_ALL, false, Hash40::new("collision_attr_normal"), *ATTACK_SOUND_LEVEL_L, *COLLISION_SOUND_ATTR_KICK, *ATTACK_REGION_OBJECT);'
                        attack_lines_with_frame.append((block_current_frame, synthetic_attack))
                        synthetic_data_added = True
                    elif is_isabelle_dash and 'FIGHTER_SHIZUE_GENERATE_ARTICLE_POT' in block_line_stripped:
                        synthetic_attack = 'ATTACK(agent, 0, 0, Hash40::new("have"), 10.0, 70, 85, 0, 42, 4.2, 0.0, 2.5, 0.0, None, None, None, 0.6, 0.0, *ATTACK_SETOFF_KIND_ON, *ATTACK_LR_CHECK_F, false, 0, 0.0, 0, true, false, false, false, false, *COLLISION_SITUATION_MASK_GA, *COLLISION_CATEGORY_MASK_ALL, *COLLISION_PART_MASK_ALL, false, Hash40::new("collision_attr_normal"), *ATTACK_SOUND_LEVEL_L, *COLLISION_SOUND_ATTR_KICK, *ATTACK_REGION_OBJECT);'
                        attack_lines_with_frame.append((block_current_frame, synthetic_attack))
                        synthetic_data_added = True

                attack_block_pattern = r'(ATTACK(?:_ABS)?)\s*\(\s*agent\s*,\s*(.*)\);?'
                if re.search(attack_block_pattern, block_line_stripped) and not block_line_stripped.startswith('//') and not block_skip_conditional_attacks:
                    attack_lines_with_frame.append((block_current_frame, block_line_stripped))

                if ('CATCH(agent,' in block_line_stripped) and not block_line_stripped.startswith('//') and not block_skip_conditional_attacks:
                    if move_type in ['grab', 'dash_grab', 'pivot_grab']:
                        attack_lines_with_frame.append((block_current_frame, 'CATCH_GRAB'))

                if is_throw_move and 'ATK_HIT_ABS' in block_line_stripped and '*FIGHTER_ATTACK_ABSOLUTE_KIND_THROW' in block_line_stripped:
                    throw_release_frame = block_current_frame
            
            i = j - 1
        
        i += 1
    
    if not synthetic_data_added:
        if is_villager_dash:
            synthetic_attack = 'ATTACK(agent, 0, 0, Hash40::new("have"), 10.0, 59, 82, 0, 45, 4.2, 0.0, 2.5, 0.0, None, None, None, 1.0, 0.0, *ATTACK_SETOFF_KIND_ON, *ATTACK_LR_CHECK_SPEED, false, 0, 0.0, 0, true, false, false, false, false, *COLLISION_SITUATION_MASK_GA, *COLLISION_CATEGORY_MASK_ALL, *COLLISION_PART_MASK_ALL, false, Hash40::new("collision_attr_normal"), *ATTACK_SOUND_LEVEL_L, *COLLISION_SOUND_ATTR_KICK, *ATTACK_REGION_OBJECT);'
            attack_lines_with_frame.append((14.0, synthetic_attack))
        elif is_isabelle_dash:
            synthetic_attack = 'ATTACK(agent, 0, 0, Hash40::new("have"), 10.0, 70, 85, 0, 42, 4.2, 0.0, 2.5, 0.0, None, None, None, 0.6, 0.0, *ATTACK_SETOFF_KIND_ON, *ATTACK_LR_CHECK_F, false, 0, 0.0, 0, true, false, false, false, false, *COLLISION_SITUATION_MASK_GA, *COLLISION_CATEGORY_MASK_ALL, *COLLISION_PART_MASK_ALL, false, Hash40::new("collision_attr_normal"), *ATTACK_SOUND_LEVEL_L, *COLLISION_SOUND_ATTR_KICK, *ATTACK_REGION_OBJECT);'
            attack_lines_with_frame.append((12.0, synthetic_attack))
    
    if not attack_lines_with_frame:
        return None

    if move_type in ['grab', 'dash_grab', 'pivot_grab']:
        catch_frames = [frame for frame, line in attack_lines_with_frame if line == 'CATCH_GRAB']
        if not catch_frames:
            return None
        
        earliest_catch_frame = min(catch_frames)
        
        real_frame = calculate_real_frame_with_motion_module(earliest_catch_frame, frame_events)
        frame_display = str(int(math.ceil(real_frame)))
        
        return (None, None, frame_display, None, None, None, None, None, None, None, None, None, "N/A")

    hitbox_data_points = []

    special_throw_exceptions = [
        ('gaogaen', 'bthrow'),
        ('tantan', 'bthrow'),
        ('plizardon', 'dthrow')
    ]
    
    for original_frame_before_attack, attack_line in attack_lines_with_frame:
        attack_pattern_match = re.search(r'(ATTACK(?:_ABS)?)\s*\(\s*agent\s*,\s*(.*)\);?', attack_line)
        if not attack_pattern_match:
            continue

        attack_type = attack_pattern_match.group(1)
        params_raw = attack_pattern_match.group(2)
        
        if (character_internal_name, move_type) in special_throw_exceptions and attack_type == 'ATTACK_ABS':
            continue

        params = []
        balance = 0
        current_param = ""
        
        for char in params_raw:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
            
            if char == ',' and balance == 0:
                params.append(current_param.strip())
                current_param = ""
            else:
                current_param += char
        
        if current_param:
            params.append(current_param.strip())

        damage_idx = -1
        angle_idx = -1
        kbg_idx = -1
        fkb_idx = -1
        bkb_idx = -1
        
        if attack_type == 'ATTACK':
            is_pikmin_attack = False
            if character_internal_name == 'pikmin' and len(params) > 5:
                for param in params[3:6]:
                    if 'p.dmg' in str(param) or 'p.angle' in str(param):
                        is_pikmin_attack = True
                        break
            
            if is_pikmin_attack:
                if len(params) >= 8:
                    damage_idx = 3
                    angle_idx = 4
                    kbg_idx = 5
                    fkb_idx = 6
                    bkb_idx = 7
            else:
                if len(params) >= 8:
                    damage_idx = 3
                    angle_idx = 4
                    kbg_idx = 5
                    fkb_idx = 6
                    bkb_idx = 7
            
        elif attack_type == 'ATTACK_ABS':
            if len(params) > 0:
                first_param = params[0].strip()
                
                if 'WEAPON_PIKMIN_PIKMIN_ATTACK_ABSOLUTE_KIND_THROW' in attack_line:
                    if len(params) >= 7:
                        damage_idx = 2
                        angle_idx = 3
                        kbg_idx = 4
                        fkb_idx = 5
                        bkb_idx = 6
                elif is_throw_move and '*FIGHTER_ATTACK_ABSOLUTE_KIND_THROW' in first_param:
                    if len(params) >= 7:
                        damage_idx = 2
                        angle_idx = 3
                        kbg_idx = 4
                        fkb_idx = 5
                        bkb_idx = 6
                elif 'FIGHTER_ATTACK_ABSOLUTE_KIND_CATCH' in first_param or \
                     'FIGHTER_ATTACK_ABSOLUTE_KIND_CATCH_SIT' in first_param:
                    if len(params) >= 10: 
                        damage_idx = 6
                        angle_idx = 7
                        kbg_idx = 8
                        fkb_idx = 9
                        bkb_idx = 10 
                    elif len(params) >= 7:
                        damage_idx = 3
                        angle_idx = 4
                        kbg_idx = 5
                        fkb_idx = 6
                else: 
                    if len(params) >= 8:
                        damage_idx = 3
                        angle_idx = 4
                        kbg_idx = 5
                        fkb_idx = 6
                        bkb_idx = 7
                    elif len(params) >= 7:
                        damage_idx = 2
                        angle_idx = 3
                        kbg_idx = 4
                        fkb_idx = 5
                        bkb_idx = 6

        current_hitbox = {
            'damage': None, 'angle': None, 'kbg': None, 'fkb': None, 'bkb': None,
            'original_frame': original_frame_before_attack,
            'attack_type': attack_type,
            'params_raw': params_raw
        }

        if character_internal_name == 'pikmin':
            red_pikmin = {'dmg': 1.05, 'angle': 0}
            
            if damage_idx != -1 and len(params) > damage_idx:
                current_hitbox['damage'] = get_numerical_value_enhanced(params[damage_idx], variable_values, red_pikmin)
            if angle_idx != -1 and len(params) > angle_idx:
                current_hitbox['angle'] = get_numerical_value_enhanced(params[angle_idx], variable_values, red_pikmin)
            if kbg_idx != -1 and len(params) > kbg_idx:
                current_hitbox['kbg'] = get_numerical_value_enhanced(params[kbg_idx], variable_values, red_pikmin)
            if fkb_idx != -1 and len(params) > fkb_idx:
                current_hitbox['fkb'] = get_numerical_value_enhanced(params[fkb_idx], variable_values, red_pikmin)
            if bkb_idx != -1 and len(params) > bkb_idx:
                current_hitbox['bkb'] = get_numerical_value_enhanced(params[bkb_idx], variable_values, red_pikmin)
        else:
            if damage_idx != -1 and len(params) > damage_idx:
                current_hitbox['damage'] = get_numerical_value(params[damage_idx], variable_values)
            if angle_idx != -1 and len(params) > angle_idx:
                current_hitbox['angle'] = get_numerical_value(params[angle_idx], variable_values)
            if kbg_idx != -1 and len(params) > kbg_idx:
                current_hitbox['kbg'] = get_numerical_value(params[kbg_idx], variable_values)
            if fkb_idx != -1 and len(params) > fkb_idx:
                current_hitbox['fkb'] = get_numerical_value(params[fkb_idx], variable_values)
            if bkb_idx != -1 and len(params) > bkb_idx:
                current_hitbox['bkb'] = get_numerical_value(params[bkb_idx], variable_values)

        if current_hitbox['damage'] is not None and current_hitbox['damage'] not in [0.0, 40.0]:
             hitbox_data_points.append(current_hitbox)
    
    if not hitbox_data_points:
        return None
    
    valid_hitboxes_for_frame = [h for h in hitbox_data_points if h['damage'] is not None and h['damage'] > 0]
    if not valid_hitboxes_for_frame:
        return None
    
    if is_throw_move and throw_release_frame is not None:
        original_frame_for_display = throw_release_frame
    elif is_throw_move:
        if valid_hitboxes_for_frame:
            latest_attack_frame = max(valid_hitboxes_for_frame, key=lambda x: x['original_frame'])['original_frame']
            original_frame_for_display = latest_attack_frame
        else:
            original_frame_for_display = 1.0
    else:
        earliest_active_hitbox = min(valid_hitboxes_for_frame, key=lambda x: x['original_frame'])
        original_frame_for_display = earliest_active_hitbox['original_frame']

    real_frame = calculate_real_frame_with_motion_module(original_frame_for_display, frame_events)
    frame_display = str(int(math.ceil(real_frame)))

    if original_frame_for_display == 0:
        if character_internal_name == 'murabito' and move_type == 'fair':
            real_frame = 9.0
            frame_display = "9"
        elif character_internal_name == 'shizue' and move_type == 'bair':
            real_frame = 12.0
            frame_display = "12"
    
    if character_internal_name == 'bayonetta':
        if move_type == 'fsmash':
            real_frame = 17.0
            frame_display = "17"
        elif move_type == 'usmash':
            real_frame = 16.0
            frame_display = "16"
        elif move_type == 'dsmash':
            real_frame = 17.0
            frame_display = "17"
    elif character_internal_name == 'murabito' and move_type == 'fsmash':
        real_frame = 20.0
        frame_display = "20"
    elif character_internal_name == 'pickel' and move_type == 'dsmash':
        steve_dsmash_frame = extract_steve_dsmash_frame_from_fallback()
        if steve_dsmash_frame:
            real_frame = steve_dsmash_frame
            frame_display = str(int(steve_dsmash_frame))
        else:
            real_frame = 8.0
            frame_display = "8"
    elif character_internal_name == 'pikmin':
        if move_type == 'fthrow':
            real_frame = 15.0
            frame_display = "15"
        elif move_type == 'bthrow':
            real_frame = 21.0
            frame_display = "21"
        elif move_type == 'uthrow':
            real_frame = 22.0
            frame_display = "22"
        elif move_type == 'dthrow':
            real_frame = 23.0
            frame_display = "23"
    elif character_internal_name == 'rockman' and move_type == 'dair':
        real_frame = 18.0
        frame_display = "18"
            
    selected_hitbox = None
    if (character_internal_name, move_type) in special_throw_exceptions:
        filtered_hitboxes = [h for h in hitbox_data_points if h['attack_type'] == 'ATTACK' and h['damage'] is not None and h['damage'] > 0]
        if filtered_hitboxes:
            selected_hitbox = min(filtered_hitboxes, key=lambda x: x['original_frame'])
        else:
            return None
    elif is_throw_move:
        earliest_active_hitbox = min(valid_hitboxes_for_frame, key=lambda x: x['original_frame'])
        selected_hitbox = earliest_active_hitbox
    else:
        valid_hitboxes_for_damage = [h for h in hitbox_data_points if h['damage'] is not None and h['damage'] > 0]
        if valid_hitboxes_for_damage:
            selected_hitbox = max(valid_hitboxes_for_damage, key=lambda x: x['damage'])
        else:
            earliest_active_hitbox = min(valid_hitboxes_for_frame, key=lambda x: x['original_frame'])
            selected_hitbox = earliest_active_hitbox

    if not selected_hitbox:
        return None

    if is_throw_move and total_throw_damage is not None and total_throw_damage > 0:
        final_damage = total_throw_damage
    else:
        final_damage = selected_hitbox.get('damage')
        
    if character_internal_name == 'plizardon' and move_type == 'dthrow':
        final_damage = 10.0   
        
    final_angle = selected_hitbox.get('angle')
    final_kbg = selected_hitbox.get('kbg')
    final_fkb = selected_hitbox.get('fkb')
    final_bkb = selected_hitbox.get('bkb')

    display_damage = "N/A"
    if final_damage is not None:
        display_damage = str(int(final_damage)) if final_damage == int(final_damage) else f"{final_damage:.1f}"

    display_angle = "N/A"
    if final_angle is not None:
        display_angle = str(int(final_angle)) if final_angle == int(final_angle) else f"{final_angle:.1f}"

    display_kbg = "N/A"
    if final_kbg is not None:
        display_kbg = str(int(final_kbg)) if final_kbg == int(final_kbg) else f"{final_kbg:.1f}"

    display_fkb = "N/A"
    if final_fkb is not None:
        display_fkb = str(int(final_fkb)) if final_fkb == int(final_fkb) else f"{final_fkb:.1f}"

    display_bkb = "N/A"
    if final_bkb is not None:
        display_bkb = str(int(final_bkb)) if final_bkb == int(final_bkb) else f"{final_bkb:.1f}"
        
    original_faf = None
    real_faf = None
    faf_display = "N/A"
    
    if character_faf_data and move_type in character_faf_data:
        original_faf = character_faf_data[move_type]
        if original_faf and original_faf > 0:
            real_faf = calculate_real_frame_with_motion_module(float(original_faf), frame_events)
            faf_display = str(int(round(real_faf)))
    
    return (final_damage, display_damage, frame_display, 
            final_angle, display_angle, 
            final_kbg, display_kbg, 
            final_fkb, display_fkb, 
            final_bkb, display_bkb, 
            real_faf, faf_display)

def find_all_attacks():
    """Main function to find and analyze all attack data for all characters."""
    base_path = r"C:\Users\Alex\Documents\GitHub\HewDraw-Remix\fighters"
    fallback_base_path = r"C:\Users\Alex\Documents\GitHub\Roy\SSBU-Dumped-Scripts\smashline-hdr"
    animations_base_path = r"C:\Users\Alex\Desktop\Animations"
    hdr_base_path = r"C:\Users\Alex\Documents\GitHub\HewDraw-Remix"
    
    landing_lag_data = parse_landing_lag_data()
    
    fighter_stats_data = parse_fighter_stats_data()
    
    attack_functions = {
        'jab1': 'game_attack11',
        'jab2': 'game_attack12', 
        'jab3': 'game_attack13',
        
        'ftilt': 'game_attacks3',
        'utilt': 'game_attackhi3',
        'dtilt': 'game_attacklw3',
        
        'fsmash': 'game_attacks4',
        'usmash': 'game_attackhi4',
        'dsmash': 'game_attacklw4',
        
        'nair': 'game_attackairn',
        'fair': 'game_attackairf',
        'bair': 'game_attackairb',
        'uair': 'game_attackairhi',
        'dair': 'game_attackairlw',
        
        'dash_attack': 'game_attackdash',
        
        'grab': 'game_catch',
        'dash_grab': 'game_catchdash',
        'pivot_grab': 'game_catchturn',
        'pummel': 'game_catchattack',
        'fthrow': 'game_throwf',
        'fthrow': 'game_throwf',
        'bthrow': 'game_throwb',
        'uthrow': 'game_throwhi',
        'dthrow': 'game_throwlw',
        
        'neutral_b': 'game_specialn',
        'side_b': 'game_specials',
        'up_b': 'game_specialhi',
        'down_b': 'game_speciallw',
        
        'neutral_b_air': 'game_specialairn',
        'side_b_air': 'game_specialairs',
        'up_b_air': 'game_specialairhi',
        'down_b_air': 'game_specialairlw',
    }
    
    fallback_file_mapping = {
        'jab1': 'Attack11.txt',
        'jab2': 'Attack12.txt', 
        'jab3': 'Attack13.txt',
        'ftilt': 'AttackS3.txt',
        'utilt': 'AttackHi3.txt',
        'dtilt': 'AttackLw3.txt',
        'fsmash': 'AttackS4.txt',
        'usmash': 'AttackHi4.txt',
        'dsmash': 'AttackLw4.txt',
        'nair': 'AttackAirN.txt',
        'fair': 'AttackAirF.txt',
        'bair': 'AttackAirB.txt',
        'uair': 'AttackAirHi.txt',
        'dair': 'AttackAirLw.txt',
        'dash_attack': 'AttackDash.txt',
        'grab': 'Catch.txt',
        'dash_grab': 'CatchDash.txt',
        'pivot_grab': 'CatchTurn.txt',
        'pummel': 'CatchAttack.txt',
        'fthrow': 'ThrowF.txt',
        'bthrow': 'ThrowB.txt',
        'uthrow': 'ThrowHi.txt',
        'dthrow': 'ThrowLw.txt',
        'neutral_b': 'SpecialN.txt',
        'side_b': 'SpecialS.txt',
        'up_b': 'SpecialHi.txt',
        'down_b': 'SpecialLw.txt',
        'neutral_b_air': 'SpecialAirN.txt',
        'side_b_air': 'SpecialAirS.txt',
        'up_b_air': 'SpecialAirHi.txt',
        'down_b_air': 'SpecialAirLw.txt',
    }
    
    skip_folders = {
        'ptrainer',
        'koopag',
        'common'
    }
    
    results = {move_type: [] for move_type in attack_functions.keys()}
    not_found = {move_type: [] for move_type in attack_functions.keys()}
    fallback_found = {move_type: [] for move_type in attack_functions.keys()}
    
    character_mapping = {
        'mario': 'Mario', 'donkey': 'Donkey Kong', 'link': 'Link', 'samus': 'Samus', 
        'samusd': 'Dark Samus', 'yoshi': 'Yoshi', 'kirby': 'Kirby', 'fox': 'Fox', 
        'pikachu': 'Pikachu', 'luigi': 'Luigi', 'ness': 'Ness', 'captain': 'Captain Falcon', 
        'purin': 'Jigglypuff', 'peach': 'Peach', 'daisy': 'Daisy', 'koopa': 'Bowser', 
        'nana': 'Ice Climbers', 'popo': 'Ice Climbers', 'iceclimber': 'Ice Climbers', 'sheik': 'Sheik', 'zelda': 'Zelda', 
        'mariod': 'Dr.Mario', 'pichu': 'Pichu', 'falco': 'Falco', 'marth': 'Marth', 
        'lucina': 'Lucina', 'younglink': 'Young Link', 'ganon': 'Ganondorf', 'mewtwo': 'Mewtwo', 
        'roy': 'Roy', 'chrom': 'Chrom', 'gamewatch': 'Mr.Game & Watch', 'metaknight': 'Meta Knight', 
        'pit': 'Pit', 'pitb': 'Dark Pit', 'szerosuit': 'Zero Suit Samus', 'wario': 'Wario', 
        'snake': 'Snake', 'ike': 'Ike', 'pzenigame': 'Squirtle', 'pfushigisou': 'Ivysaur', 
        'plizardon': 'Charizard', 'diddy': 'Diddy Kong', 'lucas': 'Lucas', 'sonic': 'Sonic', 
        'dedede': 'King Dedede', 'pikmin': 'Olimar', 'lucario': 'Lucario', 'robot': 'R.O.B.', 
        'toonlink': 'Toon Link', 'wolf': 'Wolf', 'murabito': 'Villager', 'rockman': 'Mega Man', 
        'wiifit': 'Wii Fit Trainer', 'rosetta': 'Rosalina & Luma', 'littlemac': 'Little Mac', 
        'gekkouga': 'Greninja', 'miifighter': 'Mii Brawler', 'miiswordsman': 'Mii Swordfighter', 
        'miigunner': 'Mii Gunner', 'palutena': 'Palutena', 'pacman': 'Pac-Man', 'reflet': 'Robin', 
        'shulk': 'Shulk', 'koopajr': 'Bowser Jr.', 'duckhunt': 'Duck Hunt', 'ryu': 'Ryu', 
        'ken': 'Ken', 'cloud': 'Cloud', 'kamui': 'Corrin', 'bayonetta': 'Bayonetta', 
        'inkling': 'Inkling', 'ridley': 'Ridley', 'simon': 'Simon', 'richter': 'Richter', 
        'krool': 'King K. Rool', 'shizue': 'Isabelle', 'gaogaen': 'Incineroar', 'packun': 'Piranha Plant', 
        'jack': 'Joker', 'brave': 'Hero', 'buddy': 'Banjo & Kazooie', 'dolly': 'Terry', 
        'master': 'Byleth', 'tantan': 'Min Min', 'pickel': 'Steve', 'edge': 'Sephiroth', 
        'eflame': 'Pyra', 'element': 'Rex', 'elight': 'Mythra', 'demon': 'Kazuya', 'trail': 'Sora'
    }
    
    def check_fallback_location(internal_name, move_type, function_name, character_faf_data=None):
        """Check the fallback location for a specific character and move with improved path detection"""
        
        possible_paths = [
            os.path.join(fallback_base_path, f"lua2cpp_{internal_name}", internal_name),
            os.path.join(fallback_base_path, f"lua2cpp_{internal_name}"),
            os.path.join(fallback_base_path, internal_name),
            os.path.join(fallback_base_path, f"{internal_name}_lua2cpp"),
        ]
        
        if internal_name in ['nana', 'popo', 'iceclimber']:
            ice_climber_paths = [
                os.path.join(fallback_base_path, "lua2cpp_popo", "popo"),
                os.path.join(fallback_base_path, "lua2cpp_nana", "nana"),
                os.path.join(fallback_base_path, "lua2cpp_popo"),
                os.path.join(fallback_base_path, "lua2cpp_nana"),
                os.path.join(fallback_base_path, "popo"),
                os.path.join(fallback_base_path, "nana"),
            ]
            possible_paths.extend(ice_climber_paths)
        
        if internal_name == 'bayonetta' and move_type in ['fsmash', 'usmash', 'dsmash']:
            bayonetta_paths = []
            for base_path in possible_paths:
                bayonetta_paths.append(os.path.join(base_path, "wickedweavearm"))
            possible_paths.extend(bayonetta_paths)
        elif internal_name == 'murabito' and move_type == 'fsmash':
            villager_paths = []
            for base_path in possible_paths:
                villager_paths.append(os.path.join(base_path, "bowlingball"))
            possible_paths.extend(villager_paths)
        elif internal_name == 'pickel' and move_type == 'dsmash':
            steve_paths = []
            for base_path in possible_paths:
                steve_paths.append(os.path.join(base_path, "pickel_melt"))
            possible_paths.extend(steve_paths)
        
        fallback_filename = fallback_file_mapping.get(move_type)
        if not fallback_filename:
            return None
        
        for path in possible_paths:
            if os.path.exists(path):
                fallback_file_path = os.path.join(path, fallback_filename)
                
                if os.path.exists(fallback_file_path):
                    try:
                        with open(fallback_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                        
                        result = analyze_function(content, function_name, move_type, internal_name, character_faf_data)
                        if result:
                            return result
                        
                    except Exception as e:
                        print(f"Error reading fallback file {fallback_file_path}: {e}")
        
        return None
    
    if not os.path.exists(base_path):
        print(f"Base path does not exist: {base_path}")
        return results, not_found, fallback_found, landing_lag_data, fighter_stats_data

    file_mappings = {
        'jab1': 'ground.rs', 'jab2': 'ground.rs', 'jab3': 'ground.rs',
        'rapid_jab': 'ground.rs', 'rapid_jab_end': 'ground.rs',
        'ftilt': 'tilts.rs', 'utilt': 'tilts.rs', 'dtilt': 'tilts.rs',
        'fsmash': 'smashes.rs', 'usmash': 'smashes.rs', 'dsmash': 'smashes.rs',
        'nair': 'aerials.rs', 'fair': 'aerials.rs', 'bair': 'aerials.rs',
        'uair': 'aerials.rs', 'dair': 'aerials.rs',
        'dash_attack': 'ground.rs',
        'grab': 'throws.rs', 'dash_grab': 'throws.rs', 'pivot_grab': 'throws.rs',
        'pummel': 'throws.rs', 'fthrow': 'throws.rs', 'bthrow': 'throws.rs',
        'uthrow': 'throws.rs', 'dthrow': 'throws.rs',
        'neutral_b': 'specials.rs', 'side_b': 'specials.rs', 'up_b': 'specials.rs', 'down_b': 'specials.rs',
        'neutral_b_air': 'specials.rs', 'side_b_air': 'specials.rs', 'up_b_air': 'specials.rs', 'down_b_air': 'specials.rs',
    }
    
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        
        if not os.path.isdir(folder_path):
            continue
        
        if folder_name in skip_folders:
            continue
        
        print(f"Processing folder: {folder_name}")
        
        if folder_name == 'nana':
            continue
        
        display_name = character_mapping.get(folder_name, folder_name)
            
        faf_lookup_name = 'popo' if folder_name == 'iceclimber' else folder_name
        character_faf_data = get_character_faf_data(faf_lookup_name, animations_base_path, hdr_base_path)
        
        for move_type, function_name in attack_functions.items():
            found_in_primary = False
            current_function_name = function_name
            current_file_path_base = os.path.join(folder_path, "src", "acmd")
            file_to_check = file_mappings.get(move_type, 'attacks.rs')
            
            if folder_name == 'rockman' and move_type == 'nair':
                current_function_name = 'game_attackairnmelee'
            elif folder_name == 'rockman' and move_type == 'ftilt':
                current_function_name = 'game_attacks3melee'
            elif folder_name == 'rockman' and move_type == 'jab1':
                current_function_name = 'game_attack11melee'
            elif folder_name == 'metaknight' and move_type == 'jab1':
                current_function_name = 'game_attack100'
            elif folder_name == 'pickel' and move_type == 'jab1':
                file_to_check = 'tilts.rs'
                current_function_name = 'game_attacks3'
            elif folder_name == 'pickel' and move_type == 'nair':
                file_to_check = 'tilts.rs'
                current_function_name = 'game_attacks3'
            elif folder_name == 'pickel' and move_type == 'dash_attack':
                current_function_name = 'game_specialsfailed'
            elif folder_name in ['nana', 'popo', 'iceclimber'] and move_type == 'pummel':
                current_function_name = 'game_catchattack_nana'
            elif folder_name == 'miigunner':
                
                current_file_path_base = os.path.join(folder_path, "src", "acmd")

                if move_type in ['nair', 'fair', 'bair', 'uair', 'dair']:
                    current_file_path_base = os.path.join(folder_path, "src", "acmd", "aerials")
                    aerial_file_mapping = {
                        'nair': 'attack_air_n.rs',
                        'fair': 'attack_air_f.rs', 
                        'bair': 'attack_air_b.rs',
                        'uair': 'attack_air_hi.rs',
                        'dair': 'attack_air_lw.rs'
                    }
                    file_to_check = aerial_file_mapping[move_type]
                elif move_type == 'neutral_b':
                    file_to_check = 'specialn.rs'
                elif move_type == 'side_b':
                    file_to_check = 'specials.rs'
                elif move_type == 'up_b':
                    file_to_check = 'specialhi.rs'
                elif move_type == 'down_b':
                    file_to_check = 'speciallw.rs'
                elif move_type == 'neutral_b_air':
                    file_to_check = 'specialairn.rs'
                elif move_type == 'side_b_air':
                    file_to_check = 'specialairs.rs'
                elif move_type == 'up_b_air':
                    file_to_check = 'specialairhi.rs'
                elif move_type == 'down_b_air':
                    file_to_check = 'specialairlw.rs'
                else:
                    file_to_check = file_mappings.get(move_type, 'attacks.rs')
                
            elif folder_name == 'murabito' and move_type == 'fair':
                current_file_path_base = os.path.join(folder_path, "src", "bullet")
                current_function_name = 'game_shootf'
                file_to_check = 'acmd.rs'
            elif folder_name == 'rockman' and move_type == 'dair':
                current_file_path_base = os.path.join(folder_path, "src", "hardknuckle")
                current_function_name = 'game_regular'
                file_to_check = 'acmd.rs'
            elif folder_name == 'shizue' and move_type == 'bair':
                current_file_path_base = os.path.join(folder_path, "src", "bullet")
                current_function_name = 'game_shootb'
                file_to_check = 'acmd.rs'
            elif folder_name == 'bayonetta' and move_type in ['fsmash', 'usmash', 'dsmash']:
                current_file_path_base = os.path.join(folder_path, "src", "wickedweavearm")
                file_to_check = 'acmd.rs'
            elif folder_name == 'murabito' and move_type == 'fsmash':
                current_file_path_base = os.path.join(folder_path, "src", "bowlingball")
                current_function_name = 'game_fall'
                file_to_check = 'acmd.rs'
            elif folder_name == 'ness' and move_type in ['usmash', 'dsmash']:
                current_file_path_base = os.path.join(folder_path, "src", "yoyohead")
                file_to_check = 'acmd.rs'
            else:
                file_to_check = file_mappings.get(move_type, 'attacks.rs')
            
            if folder_name == 'pickel' and move_type == 'dtilt':
                normal_file_path = os.path.join(folder_path, "src", "acmd", "tilts.rs")
                steve_dtilt_frame = None
                
                if os.path.exists(normal_file_path):
                    try:
                        with open(normal_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            normal_content = file.read()
                        
                        steve_dtilt_frame = extract_steve_dtilt_frame(normal_content)
                    except Exception as e:
                        print(f"Error reading normal file for Steve dtilt frame: {e}")
                
                fire_file_path = os.path.join(folder_path, "src", "fire", "acmd.rs")
                fire_result = None
                
                if os.path.exists(fire_file_path):
                    try:
                        with open(fire_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            fire_content = file.read()
                        
                        fire_result = analyze_function(fire_content, current_function_name, move_type, folder_name, character_faf_data)
                        
                    except Exception as e:
                        print(f"Error reading fire file for Steve dtilt damage: {e}")
                
                if fire_result and steve_dtilt_frame is not None:
                    (final_damage, display_damage, _, 
                     final_angle, display_angle, 
                     final_kbg, display_kbg, 
                     final_fkb, display_fkb, 
                     final_bkb, display_bkb,
                     real_faf, faf_display) = fire_result
                    
                    frame_display = str(int(round(steve_dtilt_frame)))
                    
                    landing_lag = 0
                    if move_type in ['nair', 'fair', 'bair', 'uair', 'dair']:
                        char_lag_data = landing_lag_data.get(display_name, {})
                        landing_lag = char_lag_data.get(move_type, 0)
                    
                    results[move_type].append((display_name, final_damage, display_damage, frame_display, 
                                              final_angle, display_angle, 
                                              final_kbg, display_kbg, 
                                              final_fkb, display_fkb, 
                                              final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                    found_in_primary = True
                elif fire_result:
                    (final_damage, display_damage, frame_display, 
                     final_angle, display_angle, 
                     final_kbg, display_kbg, 
                     final_fkb, display_fkb, 
                     final_bkb, display_bkb,
                     real_faf, faf_display) = fire_result
                    
                    landing_lag = 0
                    if move_type in ['nair', 'fair', 'bair', 'uair', 'dair']:
                        char_lag_data = landing_lag_data.get(display_name, {})
                        landing_lag = char_lag_data.get(move_type, 0)
                    
                    results[move_type].append((display_name, final_damage, display_damage, frame_display, 
                                              final_angle, display_angle, 
                                              final_kbg, display_kbg, 
                                              final_fkb, display_fkb, 
                                              final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                    found_in_primary = True
                
                continue
            
            if folder_name == 'miigunner' and move_type == 'fair':
                normal_file_path = os.path.join(folder_path, "src", "acmd", "aerials", "attack_air_f.rs")
                miigunner_fair_frame = None
                
                if os.path.exists(normal_file_path):
                    try:
                        with open(normal_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            normal_content = file.read()
                        
                        miigunner_fair_frame = extract_miigunner_fair_frame(normal_content)
                    except Exception as e:
                        print(f"Error reading normal file for Mii Gunner fair frame: {e}")
                
                bullet_file_path = os.path.join(folder_path, "src", "attackairf_bullet", "acmd.rs")
                bullet_result = None
                
                if os.path.exists(bullet_file_path):
                    try:
                        with open(bullet_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            bullet_content = file.read()
                        
                        bullet_result = analyze_function(bullet_content, 'game_fly', move_type, folder_name, character_faf_data)
                        
                    except Exception as e:
                        print(f"Error reading bullet file for Mii Gunner fair damage: {e}")
                
                if bullet_result and miigunner_fair_frame is not None:
                    (final_damage, display_damage, _, 
                     final_angle, display_angle, 
                     final_kbg, display_kbg, 
                     final_fkb, display_fkb, 
                     final_bkb, display_bkb,
                     real_faf, faf_display) = bullet_result
                    
                    frame_display = str(int(round(miigunner_fair_frame)))
                    
                    char_lag_data = landing_lag_data.get(display_name, {})
                    landing_lag = char_lag_data.get(move_type, 0)
                    
                    results[move_type].append((display_name, final_damage, display_damage, frame_display, 
                                              final_angle, display_angle, 
                                              final_kbg, display_kbg, 
                                              final_fkb, display_fkb, 
                                              final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                    found_in_primary = True
                elif bullet_result:
                    (final_damage, display_damage, frame_display, 
                     final_angle, display_angle, 
                     final_kbg, display_kbg, 
                     final_fkb, display_fkb, 
                     final_bkb, display_bkb,
                     real_faf, faf_display) = bullet_result
                    
                    char_lag_data = landing_lag_data.get(display_name, {})
                    landing_lag = char_lag_data.get(move_type, 0)
                    
                    results[move_type].append((display_name, final_damage, display_damage, frame_display, 
                                              final_angle, display_angle, 
                                              final_kbg, display_kbg, 
                                              final_fkb, display_fkb, 
                                              final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                    found_in_primary = True
                
                continue
            
            if folder_name == 'rockman' and move_type == 'uair':
                normal_file_path = os.path.join(folder_path, "src", "acmd", "aerials.rs")
                megaman_uair_frame = None
                
                if os.path.exists(normal_file_path):
                    try:
                        with open(normal_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            normal_content = file.read()
                        
                        megaman_uair_frame = extract_megaman_uair_frame(normal_content)
                    except Exception as e:
                        print(f"Error reading normal file for Mega Man uair frame: {e}")
                
                airshooter_file_path = os.path.join(folder_path, "src", "airshooter", "acmd.rs")
                airshooter_result = None
                
                if os.path.exists(airshooter_file_path):
                    try:
                        with open(airshooter_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            airshooter_content = file.read()
                        
                        airshooter_result = analyze_function(airshooter_content, 'game_regular', move_type, folder_name, character_faf_data)
                        
                    except Exception as e:
                        print(f"Error reading airshooter file for Mega Man uair damage: {e}")
                
                if airshooter_result and megaman_uair_frame is not None:
                    (final_damage, display_damage, _, 
                     final_angle, display_angle, 
                     final_kbg, display_kbg, 
                     final_fkb, display_fkb, 
                     final_bkb, display_bkb,
                     real_faf, faf_display) = airshooter_result
                    
                    frame_display = str(int(round(megaman_uair_frame)))
                    
                    char_lag_data = landing_lag_data.get(display_name, {})
                    landing_lag = char_lag_data.get(move_type, 0)
                    
                    results[move_type].append((display_name, final_damage, display_damage, frame_display, 
                                              final_angle, display_angle, 
                                              final_kbg, display_kbg, 
                                              final_fkb, display_fkb, 
                                              final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                    found_in_primary = True
                elif airshooter_result:
                    (final_damage, display_damage, frame_display, 
                     final_angle, display_angle, 
                     final_kbg, display_kbg, 
                     final_fkb, display_fkb, 
                     final_bkb, display_bkb,
                     real_faf, faf_display) = airshooter_result
                    
                    char_lag_data = landing_lag_data.get(display_name, {})
                    landing_lag = char_lag_data.get(move_type, 0)
                    
                    results[move_type].append((display_name, final_damage, display_damage, frame_display, 
                                              final_angle, display_angle, 
                                              final_kbg, display_kbg, 
                                              final_fkb, display_fkb, 
                                              final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                    found_in_primary = True
                
                continue
            
            if folder_name == 'pickel' and move_type == 'dair':
                steve_dair_variants = [
                    ('game_fallattack', 'Steve - Release*'),
                    ('game_fallattackride', 'Steve - Ride*')
                ]
                
                steve_dair_frame = extract_steve_dair_frame_from_fallback()
                
                forge_file_path = os.path.join(folder_path, "src", "forge", "acmd.rs")
                
                if os.path.exists(forge_file_path):
                    try:
                        with open(forge_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            forge_content = file.read()
                        
                        for variant_function, variant_display_name in steve_dair_variants:
                            if variant_function == 'game_fallattack':
                                synthetic_result = (8.0, "8.0+", str(int(steve_dair_frame)), 70, "70", 100.0, "100-", 0, "0", 62, "62")
                            else:
                                synthetic_result = (12.0, "12.0+", str(int(steve_dair_frame)), 70, "70", 100.0, "100-", 0, "0", 62, "62")
                            
                            char_lag_data = landing_lag_data.get('Steve', {})
                            landing_lag = char_lag_data.get(move_type, 0)
                            
                            results[move_type].append((variant_display_name, synthetic_result[0], synthetic_result[1], synthetic_result[2], 
                                                      synthetic_result[3], synthetic_result[4], 
                                                      synthetic_result[5], synthetic_result[6], 
                                                      synthetic_result[7], synthetic_result[8], 
                                                      synthetic_result[9], synthetic_result[10], landing_lag, real_faf, faf_display))
                            found_in_primary = True
                            
                    except Exception as e:
                        print(f"Error reading forge file for Steve dair: {e}")
                
                continue
            
            if folder_name == 'pikmin' and move_type in ['fsmash', 'usmash', 'dsmash']:
                    
                pikmin_data = parse_pikmin_info(folder_path)

                pikmin_smash_file_path = os.path.join(folder_path, "src", "pikmin", "acmd", "smashes.rs")
                
                if move_type == 'fsmash':
                    current_function_name = 'game_attacks4sjump'
                
                fallback_frame = extract_olimar_smash_frame_from_fallback(fallback_base_path, folder_name, move_type, function_name)
                
                if os.path.exists(pikmin_smash_file_path):
                    try:
                        with open(pikmin_smash_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                        
                        base_result = analyze_function(content, current_function_name, move_type, folder_name, character_faf_data)
                            
                        base_damage_values = extract_olimar_base_damage(content, current_function_name, move_type)
                        
                        if base_result and pikmin_data:
                            (_, _, base_frame, base_angle, _, base_kbg, _, base_fkb, _, base_bkb, _, base_real_faf, base_faf_display) = base_result
                            
                            final_frame = str(int(fallback_frame)) if fallback_frame else base_frame
                            
                            base_damage = base_damage_values.get('base', base_damage_values.get('initial', 15.0))
                            
                            for pikmin_id, pikmin_info in pikmin_data.items():
                                pikmin_name = pikmin_info['name']
                                dmg_mult = pikmin_info['dmg']
                                angle_mod = pikmin_info['angle']
                                
                                modified_damage = base_damage * dmg_mult
                                if move_type == 'fsmash':
                                    modified_angle = base_angle
                                else:
                                    modified_angle = base_angle + angle_mod
                                
                                display_damage = f"{modified_damage:.1f}*"
                                if move_type == 'fsmash':
                                    display_angle = str(int(modified_angle))
                                else:
                                    display_angle = f"{int(modified_angle)}*"
                                
                                variant_display_name = f"Olimar - {pikmin_name}*"
                                
                                landing_lag = 0
                                
                                results[move_type].append((variant_display_name, modified_damage, display_damage, final_frame, 
                                                          modified_angle, display_angle, 
                                                          base_kbg, str(int(base_kbg)) if base_kbg == int(base_kbg) else f"{base_kbg:.1f}", 
                                                          base_fkb, str(int(base_fkb)) if base_fkb == int(base_fkb) else f"{base_fkb:.1f}", 
                                                          base_bkb, str(int(base_bkb)) if base_bkb == int(base_bkb) else f"{base_bkb:.1f}", landing_lag, base_real_faf, base_faf_display))
                                found_in_primary = True
                                
                        else:
                            print(f"DEBUG: Failed to get base result or pikmin data for Olimar {move_type}")
                            
                    except Exception as e:
                        print(f"DEBUG: Error reading file {file_path} for Olimar {move_type}: {e}")
                else:
                    print(f"DEBUG: File does not exist: {file_path}")
                
                if found_in_primary:
                    continue
            
            if folder_name == 'pikmin' and move_type in ['nair', 'fair', 'bair', 'uair', 'dair']:
                
                file_path = os.path.join(current_file_path_base, file_to_check)
                
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                        
                        regular_result = analyze_function(content, current_function_name, move_type, folder_name, character_faf_data)
                        
                        if regular_result:
                            (final_damage, display_damage, frame_display, 
                             final_angle, display_angle, 
                             final_kbg, display_kbg, 
                             final_fkb, display_fkb, 
                             final_bkb, display_bkb,
                             real_faf, faf_display) = regular_result
                            
                            char_lag_data = landing_lag_data.get('Olimar', {})
                            landing_lag = char_lag_data.get(move_type, 0)
                            
                            results[move_type].append(("Olimar - No Pikmin", final_damage, display_damage, frame_display, 
                                                      final_angle, display_angle, 
                                                      final_kbg, display_kbg, 
                                                      final_fkb, display_fkb, 
                                                      final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                            found_in_primary = True
                            
                    except Exception as e:
                        print(f"DEBUG: Error reading regular file for Olimar {move_type}: {e}")
                else:
                    print(f"DEBUG: Regular aerial file does not exist: {file_path}")
                
                pikmin_aerial_file_path = os.path.join(folder_path, "src", "pikmin", "acmd", "aerials.rs")
                
                if os.path.exists(pikmin_aerial_file_path):
                    try:
                        with open(pikmin_aerial_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            pikmin_content = file.read()
                        
                        pikmin_result = analyze_function(pikmin_content, current_function_name, move_type, folder_name, character_faf_data)
                        pikmin_damage_values = extract_olimar_base_damage(pikmin_content, current_function_name, move_type)
                        pikmin_data = parse_pikmin_info(folder_path)
                        
                        if pikmin_result and pikmin_data:
                            (_, _, pikmin_frame, pikmin_base_angle, _, pikmin_kbg, _, pikmin_fkb, _, pikmin_bkb, _, _, _) = pikmin_result
                            
                            base_damage = pikmin_damage_values.get('base', pikmin_result[0])
                            
                            for pikmin_id, pikmin_info in pikmin_data.items():
                                pikmin_name = pikmin_info['name']
                                dmg_mult = pikmin_info['dmg']
                                angle_mod = pikmin_info['angle']
                                
                                modified_damage = base_damage * dmg_mult
                                modified_angle = pikmin_base_angle + angle_mod
                                
                                display_damage = f"{modified_damage:.1f}*"
                                if move_type == 'fsmash':
                                    display_angle = str(int(modified_angle))
                                else:
                                    display_angle = f"{int(modified_angle)}*"
                                
                                variant_display_name = f"Olimar - {pikmin_name}*"
                                
                                char_lag_data = landing_lag_data.get('Olimar', {})
                                landing_lag = char_lag_data.get(move_type, 0)
                                
                                results[move_type].append((variant_display_name, modified_damage, display_damage, pikmin_frame, 
                                                          modified_angle, display_angle, 
                                                          pikmin_kbg, str(int(pikmin_kbg)) if pikmin_kbg == int(pikmin_kbg) else f"{pikmin_kbg:.1f}", 
                                                          pikmin_fkb, str(int(pikmin_fkb)) if pikmin_fkb == int(pikmin_fkb) else f"{pikmin_fkb:.1f}", 
                                                          pikmin_bkb, str(int(pikmin_bkb)) if pikmin_bkb == int(pikmin_bkb) else f"{pikmin_bkb:.1f}", landing_lag, real_faf, faf_display))
                                found_in_primary = True
                        else:
                            print(f"DEBUG: Failed to get Pikmin result or data for {move_type}")
                                
                    except Exception as e:
                        print(f"DEBUG: Error reading Pikmin aerial file for Olimar {move_type}: {e}")
                else:
                    print(f"DEBUG: Pikmin aerial file does not exist: {pikmin_aerial_file_path}")
                
                if found_in_primary:
                    continue
            
            if folder_name == 'pikmin' and move_type in ['fthrow', 'bthrow', 'uthrow', 'dthrow']:

                pikmin_data = parse_pikmin_info(folder_path)

                pikmin_throw_file_path = os.path.join(folder_path, "src", "pikmin", "acmd", "throws.rs")
                
                fallback_frame_mapping = {
                    'fthrow': 15.0,
                    'bthrow': 21.0,
                    'uthrow': 22.0, 
                    'dthrow': 23.0
                }
                final_frame = str(int(fallback_frame_mapping.get(move_type, 15.0)))
                
                if os.path.exists(pikmin_throw_file_path):
                    try:
                        with open(pikmin_throw_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                        
                        base_result = analyze_function(content, current_function_name, move_type, folder_name, character_faf_data)
                        base_damage_values = extract_olimar_throw_base_damage(content, current_function_name, move_type)
                        
                        if base_result and base_damage_values and pikmin_data:
                            (_, _, base_frame, base_angle, _, base_kbg, _, base_fkb, _, base_bkb, _, base_real_faf, base_faf_display) = base_result
                            
                            for pikmin_id, pikmin_info in pikmin_data.items():
                                pikmin_name = pikmin_info['name']
                                dmg_mult = pikmin_info['dmg']
                                angle_mod = pikmin_info['angle']
                                
                                if pikmin_name == 'Blue':
                                    base_damage = base_damage_values['blue']
                                else:
                                    base_damage = base_damage_values['other']
                                
                                modified_damage = base_damage * dmg_mult
                                modified_angle = base_angle + angle_mod
                                
                                display_damage = f"{modified_damage:.1f}*"
                                display_angle = f"{int(modified_angle)}*"
                                
                                variant_display_name = f"Olimar - {pikmin_name}*"
                                
                                landing_lag = 0
                                
                                raw_faf = character_faf_data.get(move_type)
                                final_faf_value = float(raw_faf) if raw_faf else None
                                final_faf_display = str(int(raw_faf)) if raw_faf else "N/A"

                                results[move_type].append((variant_display_name, modified_damage, display_damage, final_frame, 
                                                          modified_angle, display_angle, 
                                                          base_kbg, str(int(base_kbg)) if base_kbg == int(base_kbg) else f"{base_kbg:.1f}", 
                                                          base_fkb, str(int(base_fkb)) if base_fkb == int(base_fkb) else f"{base_fkb:.1f}", 
                                                          base_bkb, str(int(base_bkb)) if base_bkb == int(base_bkb) else f"{base_bkb:.1f}", 
                                                          landing_lag, final_faf_value, final_faf_display))
                                found_in_primary = True
                                
                        else:
                            print(f"DEBUG: Failed to get base result or damage values for Olimar {move_type}")
                            
                    except Exception as e:
                        print(f"DEBUG: Error reading file {pikmin_throw_file_path} for Olimar {move_type}: {e}")
                else:
                    print(f"DEBUG: File does not exist: {pikmin_throw_file_path}")
                
                if found_in_primary:
                    continue

            if folder_name == 'donkey' and move_type == 'fthrow':
                dk_throw_variants = [
                    ('game_throwff', 'Donkey Kong - Forward', 'throw_f_f'),
                    ('game_throwfb', 'Donkey Kong - Back', 'throw_f_b'),
                    ('game_throwfhi', 'Donkey Kong - High', 'throw_f_hi'),
                    ('game_throwflw', 'Donkey Kong - Low', 'throw_f_lw')
                ]
                
                file_path = os.path.join(current_file_path_base, file_to_check)
                
                for variant_function, variant_display_name, motion_key in dk_throw_variants:
                    variant_faf = None
                    variant_real_faf = None
                    variant_faf_display = "N/A"
                    
                    character_animations_path = os.path.join(animations_base_path, folder_name, 'body')
                    motion_list_path = os.path.join(character_animations_path, 'motion_list.yml')
                    hdr_motion_path = os.path.join(hdr_base_path, 'romfs', 'source', 'fighter', folder_name, 'motion', 'body', 'motion_patch.yaml')
                    
                    motion_data = {}
                    if os.path.exists(motion_list_path):
                        motion_data = parse_motion_list_yml(motion_list_path)
                    
                    if os.path.exists(hdr_motion_path):
                        patch_data = parse_motion_list_yml(hdr_motion_path)
                        for motion_key_patch, patch_info in patch_data.items():
                            if motion_key_patch in motion_data:
                                if patch_info.get('cancel_frame') is not None:
                                    motion_data[motion_key_patch]['cancel_frame'] = patch_info['cancel_frame']
                            else:
                                motion_data[motion_key_patch] = patch_info
                    
                    if motion_key in motion_data:
                        cancel_frame = motion_data[motion_key].get('cancel_frame')
                        if cancel_frame and cancel_frame > 0:
                            variant_faf = cancel_frame
                            variant_real_faf = float(variant_faf)
                            variant_faf_display = str(int(variant_faf))
                    
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                                content = file.read()
                            
                            result = analyze_function(content, variant_function, move_type, folder_name, character_faf_data)
                            if result:
                                (final_damage, display_damage, frame_display, 
                                 final_angle, display_angle, 
                                 final_kbg, display_kbg, 
                                 final_fkb, display_fkb, 
                                 final_bkb, display_bkb,
                                 real_faf, faf_display) = result
                                
                                if variant_faf_display != "N/A":
                                    real_faf = variant_real_faf
                                    faf_display = variant_faf_display
                                
                                landing_lag = 0
                                
                                results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                          final_angle, display_angle, 
                                                          final_kbg, display_kbg, 
                                                          final_fkb, display_fkb, 
                                                          final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                                found_in_primary = True
                                
                        except Exception as e:
                            print(f"Error reading file {file_path} for {variant_display_name} {move_type}: {e}")
                
                if not found_in_primary:
                    for variant_function, variant_display_name, motion_key in dk_throw_variants:
                        fallback_mapping = {
                            'game_throwff': 'ThrowFF.txt',
                            'game_throwfb': 'ThrowFB.txt', 
                            'game_throwfhi': 'ThrowFHi.txt',
                            'game_throwflw': 'ThrowFLw.txt'
                        }
                        
                        variant_faf = None
                        variant_real_faf = None
                        variant_faf_display = "N/A"
                        
                        character_animations_path = os.path.join(animations_base_path, folder_name, 'body')
                        motion_list_path = os.path.join(character_animations_path, 'motion_list.yml')
                        hdr_motion_path = os.path.join(hdr_base_path, 'romfs', 'source', 'fighter', folder_name, 'motion', 'body', 'motion_patch.yaml')
                        
                        motion_data = {}
                        if os.path.exists(motion_list_path):
                            motion_data = parse_motion_list_yml(motion_list_path)
                        
                        if os.path.exists(hdr_motion_path):
                            patch_data = parse_motion_list_yml(hdr_motion_path)
                            for motion_key_patch, patch_info in patch_data.items():
                                if motion_key_patch in motion_data:
                                    if patch_info.get('cancel_frame') is not None:
                                        motion_data[motion_key_patch]['cancel_frame'] = patch_info['cancel_frame']
                                else:
                                    motion_data[motion_key_patch] = patch_info
                        
                        if motion_key in motion_data:
                            cancel_frame = motion_data[motion_key].get('cancel_frame')
                            if cancel_frame and cancel_frame > 0:
                                variant_faf = cancel_frame
                                variant_real_faf = float(variant_faf)
                                variant_faf_display = str(int(variant_faf))
                        
                        original_mapping = fallback_file_mapping.get('fthrow')
                        fallback_file_mapping['fthrow'] = fallback_mapping.get(variant_function, 'ThrowF.txt')
                        
                        fallback_result = check_fallback_location(folder_name, move_type, variant_function, character_faf_data)
                        
                        fallback_file_mapping['fthrow'] = original_mapping
                        
                        if fallback_result:
                            (final_damage, display_damage, frame_display, 
                             final_angle, display_angle, 
                             final_kbg, display_kbg, 
                             final_fkb, display_fkb, 
                             final_bkb, display_bkb,
                             real_faf, faf_display) = fallback_result
                            
                            if variant_faf_display != "N/A":
                                real_faf = variant_real_faf
                                faf_display = variant_faf_display
                            
                            landing_lag = 0
                            
                            results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                      final_angle, display_angle, 
                                                      final_kbg, display_kbg, 
                                                      final_fkb, display_fkb, 
                                                      final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                            fallback_found[move_type].append(variant_display_name)
                        else:
                            not_found[move_type].append(variant_display_name)
                            
                continue
            
            if folder_name == 'snake' and move_type == 'fsmash':
                snake_fsmash_variants = [
                    ('game_attacks4', 'Snake - First'),
                    ('game_attacks4s2', 'Snake - Second'),
                    ('game_attacks4s3', 'Snake - Third')
                ]
                
                file_path = os.path.join(current_file_path_base, file_to_check)
                
                for variant_function, variant_display_name in snake_fsmash_variants:
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                                content = file.read()
                            
                            result = analyze_function(content, variant_function, move_type, folder_name, character_faf_data)
                            if result:
                                (final_damage, display_damage, frame_display, 
                                 final_angle, display_angle, 
                                 final_kbg, display_kbg, 
                                 final_fkb, display_fkb, 
                                 final_bkb, display_bkb,
                                 real_faf, faf_display) = result
                                
                                landing_lag = 0
                                
                                results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                          final_angle, display_angle, 
                                                          final_kbg, display_kbg, 
                                                          final_fkb, display_fkb, 
                                                          final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                                found_in_primary = True
                                
                        except Exception as e:
                            print(f"Error reading file {file_path} for {variant_display_name} {move_type}: {e}")
                
                continue
            
            if folder_name == 'link' and move_type == 'fsmash':
                link_fsmash_variants = [
                    ('game_attacks4', 'Link - First'),
                    ('game_attacks4s2', 'Link - Second')
                ]
                
                file_path = os.path.join(current_file_path_base, file_to_check)
                
                for variant_function, variant_display_name in link_fsmash_variants:
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                                content = file.read()
                            
                            result = analyze_function(content, variant_function, move_type, folder_name, character_faf_data)
                            if result:
                                (final_damage, display_damage, frame_display, 
                                 final_angle, display_angle, 
                                 final_kbg, display_kbg, 
                                 final_fkb, display_fkb, 
                                 final_bkb, display_bkb,
                                 real_faf, faf_display) = result
                                
                                landing_lag = 0
                                
                                results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                          final_angle, display_angle, 
                                                          final_kbg, display_kbg, 
                                                          final_fkb, display_fkb, 
                                                          final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                                found_in_primary = True
                                
                        except Exception as e:
                            print(f"Error reading file {file_path} for {variant_display_name} {move_type}: {e}")
                
                continue
            
            if folder_name == 'ryu' and move_type in ['jab1', 'jab2', 'jab3']:
                ryu_jab_variants = []
                
                if move_type == 'jab1':
                    ryu_jab_variants = [
                        ('game_attack11w', 'Ryu - Weak'),
                        ('game_attack11s', 'Ryu - Strong')
                    ]
                elif move_type == 'jab2':
                    ryu_jab_variants = [
                        ('game_attack12', 'Ryu - Weak'),
                        ('game_attack12s', 'Ryu - Strong')
                    ]
                elif move_type == 'jab3':
                    ryu_jab_variants = [
                        ('game_attack13', 'Ryu - Weak')
                    ]
                
                ryu_jab_file_path = os.path.join(folder_path, "src", "acmd", "ground.rs")
                
                for variant_function, variant_display_name in ryu_jab_variants:
                    if os.path.exists(ryu_jab_file_path):
                        try:
                            with open(ryu_jab_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                                content = file.read()
                            
                            result = analyze_function(content, variant_function, move_type, folder_name, character_faf_data)
                            if result:
                                (final_damage, display_damage, frame_display, 
                                 final_angle, display_angle, 
                                 final_kbg, display_kbg, 
                                 final_fkb, display_fkb, 
                                 final_bkb, display_bkb,
                                 real_faf, faf_display) = result
                                
                                landing_lag = 0
                                
                                results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                          final_angle, display_angle, 
                                                          final_kbg, display_kbg, 
                                                          final_fkb, display_fkb, 
                                                          final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                                found_in_primary = True
                                
                        except Exception as e:
                            print(f"Error reading file {ryu_jab_file_path} for {variant_display_name} {move_type}: {e}")
                
                if not found_in_primary:
                    for variant_function, variant_display_name in ryu_jab_variants:
                        fallback_result = check_fallback_location(folder_name, move_type, variant_function, character_faf_data)
                        
                        if fallback_result:
                            (final_damage, display_damage, frame_display, 
                             final_angle, display_angle, 
                             final_kbg, display_kbg, 
                             final_fkb, display_fkb, 
                             final_bkb, display_bkb,
                             real_faf, faf_display) = fallback_result
                            
                            landing_lag = 0
                            
                            results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                      final_angle, display_angle, 
                                                      final_kbg, display_kbg, 
                                                      final_fkb, display_fkb, 
                                                      final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                            fallback_found[move_type].append(variant_display_name)
                        else:
                            not_found[move_type].append(variant_display_name)
                
                continue
            
            if folder_name == 'ken' and move_type in ['jab1', 'jab2']:
                ken_jab_variants = []
                
                if move_type == 'jab1':
                    ken_jab_variants = [
                        ('game_attack11w', 'Ken - Weak'),
                        ('game_attack11s', 'Ken - Strong')
                    ]
                elif move_type == 'jab2':
                    ken_jab_variants = [
                        ('game_attack12', 'Ken - Weak')
                    ]
                
                ken_jab_file_path = os.path.join(folder_path, "src", "acmd", "ground.rs")
                
                for variant_function, variant_display_name in ken_jab_variants:
                    if os.path.exists(ken_jab_file_path):
                        try:
                            with open(ken_jab_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                                content = file.read()
                            
                            result = analyze_function(content, variant_function, move_type, folder_name, character_faf_data)
                            if result:
                                (final_damage, display_damage, frame_display, 
                                 final_angle, display_angle, 
                                 final_kbg, display_kbg, 
                                 final_fkb, display_fkb, 
                                 final_bkb, display_bkb,
                                 real_faf, faf_display) = result
                                
                                landing_lag = 0
                                
                                results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                          final_angle, display_angle, 
                                                          final_kbg, display_kbg, 
                                                          final_fkb, display_fkb, 
                                                          final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                                found_in_primary = True
                                
                        except Exception as e:
                            print(f"Error reading file {ken_jab_file_path} for {variant_display_name} {move_type}: {e}")
                
                if not found_in_primary:
                    for variant_function, variant_display_name in ken_jab_variants:
                        fallback_result = check_fallback_location(folder_name, move_type, variant_function, character_faf_data)
                        
                        if fallback_result:
                            (final_damage, display_damage, frame_display, 
                             final_angle, display_angle, 
                             final_kbg, display_kbg, 
                             final_fkb, display_fkb, 
                             final_bkb, display_bkb,
                             real_faf, faf_display) = fallback_result
                            
                            landing_lag = 0
                            
                            results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                      final_angle, display_angle, 
                                                      final_kbg, display_kbg, 
                                                      final_fkb, display_fkb, 
                                                      final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                            fallback_found[move_type].append(variant_display_name)
                        else:
                            not_found[move_type].append(variant_display_name)
                
                continue
                
            if folder_name == 'ryu' and move_type in ['ftilt', 'utilt', 'dtilt']:
                ryu_tilt_variants = []
                
                if move_type == 'ftilt':
                    ryu_tilt_variants = [
                        ('game_attacks3w', 'Ryu - Weak', 'attack_s3_s_w'),
                        ('game_attacks3s', 'Ryu - Strong', 'attack_s3_s_s')
                    ]
                elif move_type == 'utilt':
                    ryu_tilt_variants = [
                        ('game_attackhi3w', 'Ryu - Weak', 'attack_hi3_w'),
                        ('game_attackhi3s', 'Ryu - Strong', 'attack_hi3_s')
                    ]
                elif move_type == 'dtilt':
                    ryu_tilt_variants = [
                        ('game_attacklw3w', 'Ryu - Weak', 'attack_lw3_w'),
                        ('game_attacklw3s', 'Ryu - Strong', 'attack_lw3_s')
                    ]
                
                ryu_tilt_file_path = os.path.join(folder_path, "src", "acmd", "tilts.rs")
                
                for variant_function, variant_display_name, motion_key in ryu_tilt_variants:
                    variant_faf = None
                    variant_real_faf = None
                    variant_faf_display = "N/A"
                    
                    if character_faf_data:
                        character_animations_path = os.path.join(animations_base_path, folder_name, 'body')
                        motion_list_path = os.path.join(character_animations_path, 'motion_list.yml')
                        hdr_motion_path = os.path.join(hdr_base_path, 'romfs', 'source', 'fighter', folder_name, 'motion', 'body', 'motion_patch.yaml')
                        
                        motion_data = {}
                        if os.path.exists(motion_list_path):
                            motion_data = parse_motion_list_yml(motion_list_path)
                        
                        if os.path.exists(hdr_motion_path):
                            patch_data = parse_motion_list_yml(hdr_motion_path)
                            for motion_key_patch, patch_info in patch_data.items():
                                if motion_key_patch in motion_data:
                                    if patch_info.get('cancel_frame') is not None:
                                        motion_data[motion_key_patch]['cancel_frame'] = patch_info['cancel_frame']
                                else:
                                    motion_data[motion_key_patch] = patch_info
                        
                        if motion_key in motion_data:
                            cancel_frame = motion_data[motion_key].get('cancel_frame')
                            if cancel_frame and cancel_frame > 0:
                                variant_faf = cancel_frame
                                variant_real_faf = float(variant_faf)
                                variant_faf_display = str(int(variant_faf))
                    
                    if os.path.exists(ryu_tilt_file_path):
                        try:
                            with open(ryu_tilt_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                                content = file.read()
                            
                            result = analyze_function(content, variant_function, move_type, folder_name, character_faf_data)
                            if result:
                                (final_damage, display_damage, frame_display, 
                                 final_angle, display_angle, 
                                 final_kbg, display_kbg, 
                                 final_fkb, display_fkb, 
                                 final_bkb, display_bkb,
                                 real_faf, faf_display) = result
                                
                                if variant_faf_display != "N/A":
                                    real_faf = variant_real_faf
                                    faf_display = variant_faf_display
                                
                                landing_lag = 0
                                
                                results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                          final_angle, display_angle, 
                                                          final_kbg, display_kbg, 
                                                          final_fkb, display_fkb, 
                                                          final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                                found_in_primary = True
                                
                        except Exception as e:
                            print(f"Error reading file {ryu_tilt_file_path} for {variant_display_name} {move_type}: {e}")
                
                if not found_in_primary:
                    for variant_function, variant_display_name, motion_key in ryu_tilt_variants:
                        variant_faf = None
                        variant_real_faf = None
                        variant_faf_display = "N/A"
                        
                        character_animations_path = os.path.join(animations_base_path, folder_name, 'body')
                        motion_list_path = os.path.join(character_animations_path, 'motion_list.yml')
                        hdr_motion_path = os.path.join(hdr_base_path, 'romfs', 'source', 'fighter', folder_name, 'motion', 'body', 'motion_patch.yaml')
                        
                        motion_data = {}
                        if os.path.exists(motion_list_path):
                            motion_data = parse_motion_list_yml(motion_list_path)
                        
                        if os.path.exists(hdr_motion_path):
                            patch_data = parse_motion_list_yml(hdr_motion_path)
                            for motion_key_patch, patch_info in patch_data.items():
                                if motion_key_patch in motion_data:
                                    if patch_info.get('cancel_frame') is not None:
                                        motion_data[motion_key_patch]['cancel_frame'] = patch_info['cancel_frame']
                                else:
                                    motion_data[motion_key_patch] = patch_info
                        
                        if motion_key in motion_data:
                            cancel_frame = motion_data[motion_key].get('cancel_frame')
                            if cancel_frame and cancel_frame > 0:
                                variant_faf = cancel_frame
                                variant_real_faf = float(variant_faf)
                                variant_faf_display = str(int(variant_faf))
                        
                        fallback_result = check_fallback_location(folder_name, move_type, variant_function, character_faf_data)
                        
                        if fallback_result:
                            (final_damage, display_damage, frame_display, 
                             final_angle, display_angle, 
                             final_kbg, display_kbg, 
                             final_fkb, display_fkb, 
                             final_bkb, display_bkb,
                             real_faf, faf_display) = fallback_result
                            
                            if variant_faf_display != "N/A":
                                real_faf = variant_real_faf
                                faf_display = variant_faf_display
                            
                            landing_lag = 0
                            
                            results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                      final_angle, display_angle, 
                                                      final_kbg, display_kbg, 
                                                      final_fkb, display_fkb, 
                                                      final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                            fallback_found[move_type].append(variant_display_name)
                        else:
                            not_found[move_type].append(variant_display_name)
                
                continue

            if folder_name == 'ken' and move_type in ['ftilt', 'utilt', 'dtilt']:
                ken_tilt_variants = []
                
                if move_type == 'ftilt':
                    ken_tilt_variants = [
                        ('game_attacks3w', 'Ken - Weak', 'attack_s3_s_w'),
                        ('game_attacks3s', 'Ken - Strong', 'attack_s3_s_s')
                    ]
                elif move_type == 'utilt':
                    ken_tilt_variants = [
                        ('game_attackhi3w', 'Ken - Weak', 'attack_hi3_w'),
                        ('game_attackhi3s', 'Ken - Strong', 'attack_hi3_s')
                    ]
                elif move_type == 'dtilt':
                    ken_tilt_variants = [
                        ('game_attacklw3w', 'Ken - Weak', 'attack_lw3_w'),
                        ('game_attacklw3s', 'Ken - Strong', 'attack_lw3_s')
                    ]
                
                ken_tilt_file_path = os.path.join(folder_path, "src", "acmd", "tilts.rs")
                
                for variant_function, variant_display_name, motion_key in ken_tilt_variants:
                    variant_faf = None
                    variant_real_faf = None
                    variant_faf_display = "N/A"
                    
                    if character_faf_data:
                        
                        character_animations_path = os.path.join(animations_base_path, folder_name, 'body')
                        motion_list_path = os.path.join(character_animations_path, 'motion_list.yml')
                        hdr_motion_path = os.path.join(hdr_base_path, 'romfs', 'source', 'fighter', folder_name, 'motion', 'body', 'motion_patch.yaml')
                        
                        motion_data = {}
                        if os.path.exists(motion_list_path):
                            motion_data = parse_motion_list_yml(motion_list_path)
                        
                        if os.path.exists(hdr_motion_path):
                            patch_data = parse_motion_list_yml(hdr_motion_path)
                            for motion_key_patch, patch_info in patch_data.items():
                                if motion_key_patch in motion_data:
                                    if patch_info.get('cancel_frame') is not None:
                                        motion_data[motion_key_patch]['cancel_frame'] = patch_info['cancel_frame']
                                else:
                                    motion_data[motion_key_patch] = patch_info
                        
                        if motion_key in motion_data:
                            cancel_frame = motion_data[motion_key].get('cancel_frame')
                            if cancel_frame and cancel_frame > 0:
                                variant_faf = cancel_frame
                                variant_real_faf = float(variant_faf)
                                variant_faf_display = str(int(variant_faf))
                    
                    if os.path.exists(ken_tilt_file_path):
                        try:
                            with open(ken_tilt_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                                content = file.read()
                            
                            result = analyze_function(content, variant_function, move_type, folder_name, character_faf_data)
                            if result:
                                (final_damage, display_damage, frame_display, 
                                 final_angle, display_angle, 
                                 final_kbg, display_kbg, 
                                 final_fkb, display_fkb, 
                                 final_bkb, display_bkb,
                                 real_faf, faf_display) = result
                                
                                if variant_faf_display != "N/A":
                                    real_faf = variant_real_faf
                                    faf_display = variant_faf_display
                                
                                landing_lag = 0
                                
                                results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                          final_angle, display_angle, 
                                                          final_kbg, display_kbg, 
                                                          final_fkb, display_fkb, 
                                                          final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                                found_in_primary = True
                                
                        except Exception as e:
                            print(f"Error reading file {ken_tilt_file_path} for {variant_display_name} {move_type}: {e}")
                
                if not found_in_primary:
                    for variant_function, variant_display_name, motion_key in ken_tilt_variants:
                        fallback_result = check_fallback_location(folder_name, move_type, variant_function, character_faf_data)
                        
                        if fallback_result:
                            (final_damage, display_damage, frame_display, 
                             final_angle, display_angle, 
                             final_kbg, display_kbg, 
                             final_fkb, display_fkb, 
                             final_bkb, display_bkb,
                             real_faf, faf_display) = fallback_result
                            
                            landing_lag = 0
                            
                            results[move_type].append((variant_display_name, final_damage, display_damage, frame_display, 
                                                      final_angle, display_angle, 
                                                      final_kbg, display_kbg, 
                                                      final_fkb, display_fkb, 
                                                      final_bkb, display_bkb, landing_lag, real_faf, faf_display))
                            fallback_found[move_type].append(variant_display_name)
                        else:
                            not_found[move_type].append(variant_display_name)
                
                continue
            
            file_path = os.path.join(current_file_path_base, file_to_check)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                    
                    result = analyze_function(content, current_function_name, move_type, folder_name, character_faf_data)
                    
                    if result:
                        (final_damage, display_damage, frame_display, 
                         final_angle, display_angle, 
                         final_kbg, display_kbg, 
                         final_fkb, display_fkb, 
                         final_bkb, display_bkb,
                         real_faf, faf_display) = result
                        
                        landing_lag = 0
                        if move_type in ['nair', 'fair', 'bair', 'uair', 'dair']:
                            char_lag_data = landing_lag_data.get(display_name, {})
                            landing_lag = char_lag_data.get(move_type, 0)
                        
                        results[move_type].append((display_name, final_damage, display_damage, frame_display, 
                                                  final_angle, display_angle, 
                                                  final_kbg, display_kbg, 
                                                  final_fkb, display_fkb, 
                                                  final_bkb, display_bkb, 
                                                  landing_lag, real_faf, faf_display))
                        found_in_primary = True
                        
                    else:
                        pass
                        
                except Exception as e:
                    print(f"Error reading file {file_path} for {display_name} {move_type}: {e}")
            else:
                pass
            
            if not found_in_primary:
                fallback_result = check_fallback_location(folder_name, move_type, function_name, character_faf_data)
                
                if fallback_result:
                    (final_damage, display_damage, frame_display, 
                     final_angle, display_angle, 
                     final_kbg, display_kbg, 
                     final_fkb, display_fkb, 
                     final_bkb, display_bkb,
                     real_faf, faf_display) = fallback_result
                    
                    landing_lag = 0
                    if move_type in ['nair', 'fair', 'bair', 'uair', 'dair']:
                        char_lag_data = landing_lag_data.get(display_name, {})
                        landing_lag = char_lag_data.get(move_type, 0)
                    
                    results[move_type].append((display_name, final_damage, display_damage, frame_display, 
                                              final_angle, display_angle, 
                                              final_kbg, display_kbg, 
                                              final_fkb, display_fkb, 
                                              final_bkb, display_bkb, 
                                              landing_lag, real_faf, faf_display))
                    fallback_found[move_type].append(display_name)
                else:
                    not_found[move_type].append(display_name)
    
    return results, not_found, fallback_found, landing_lag_data, fighter_stats_data

def generate_tooltip_content(char_name, move_type, char_data):
    """Generate tooltip content for special characters like Steve and Olimar"""
    
    if 'Steve -' in char_name and '*' in char_name and move_type == 'dair':
        if 'Release' in char_name:
            return """<strong>Steve Dair - Release Mode</strong><br>
                     <em>Damage:</em> 8.0 + (fall_distance ÷ 5.0)<br>
                     <em>KBG:</em> 100 - (fall_distance ÷ 1.5)<br>
                     <em>Note:</em> Fall distance measured from anvil generation"""
        elif 'Ride' in char_name:
            return """<strong>Steve Dair - Ride Mode</strong><br>
                     <em>Damage:</em> 12.0 + (fall_distance ÷ 5.0)<br>
                     <em>KBG:</em> 100 - (fall_distance ÷ 1.5)<br>
                     <em>Note:</em> Fall distance measured from anvil generation"""
    
    elif 'Olimar -' in char_name and '*' in char_name:
        actual_damage = char_data[1]
        actual_angle = char_data[4]
        
        pikmin_info = {}
        if 'Red' in char_name:
            pikmin_info = {'name': 'Red Pikmin', 'dmg_mult': 1.05, 'angle_mod': 0}
            base_damage = actual_damage / 1.05
            base_angle = actual_angle - 0
        elif 'Yellow' in char_name:
            pikmin_info = {'name': 'Yellow Pikmin', 'dmg_mult': 0.94, 'angle_mod': 8}
            base_damage = actual_damage / 0.94
            base_angle = actual_angle - 8
        elif 'Blue' in char_name:
            pikmin_info = {'name': 'Blue Pikmin', 'dmg_mult': 1.00, 'angle_mod': 0}
            base_damage = actual_damage / 1.00
            base_angle = actual_angle - 0
        elif 'White' in char_name:
            pikmin_info = {'name': 'White Pikmin', 'dmg_mult': 0.75, 'angle_mod': 0}
            base_damage = actual_damage / 0.75
            base_angle = actual_angle - 0
        elif 'Purple' in char_name:
            pikmin_info = {'name': 'Purple Pikmin', 'dmg_mult': 1.20, 'angle_mod': 0}
            base_damage = actual_damage / 1.20
            base_angle = actual_angle - 0
        else:
            return None
        
        dmg_mult_str = f"×{pikmin_info['dmg_mult']:.2f}".rstrip('0').rstrip('.')
        angle_mod_str = f"+{pikmin_info['angle_mod']}°" if pikmin_info['angle_mod'] != 0 else "+0°"
        
        move_name_map = {
            'nair': 'Neutral Air', 'fair': 'Forward Air', 'bair': 'Back Air',
            'uair': 'Up Air', 'dair': 'Down Air', 'fsmash': 'Forward Smash',
            'usmash': 'Up Smash', 'dsmash': 'Down Smash',
            'fthrow': 'Forward Throw', 'bthrow': 'Back Throw', 
            'uthrow': 'Up Throw', 'dthrow': 'Down Throw'
        }
        move_display = move_name_map.get(move_type, move_type.title())
        
        throw_note = ""
        if move_type in ['fthrow', 'bthrow', 'uthrow', 'dthrow']:
            if 'Blue' in char_name:
                throw_note = "<br><em>Note:</em> Blue Pikmin has higher base damage"
            else:
                throw_note = "<br><em>Note:</em> Blue Pikmin gets different base damage"
        
        tooltip_content = f"""<strong>{pikmin_info['name']} - {move_display}</strong><br>
                             <em>Base Damage:</em> {base_damage:.1f}<br>
                             <em>Base Angle:</em> {int(base_angle)}°<br>
                             <em>Damage Multiplier:</em> {dmg_mult_str}<br>"""
        
        if pikmin_info['angle_mod'] != 0:
            tooltip_content += f"<em>Angle Modifier:</em> {angle_mod_str}<br>"
        
        tooltip_content += f"""<em>Final Damage:</em> {actual_damage:.1f}<br>
                              <em>Final Angle:</em> {int(actual_angle)}°{throw_note}"""
        
        return tooltip_content
    
    return None

def generate_html_files(results, not_found, fallback_found, fighter_stats_data):
    """Generate HTML files for each move type with tooltip functionality"""
    
    def generate_section_dropdown(current_move, category_info):
        """Generate dropdown HTML for section navigation"""
        dropdown_id = f"dropdown_{current_move}"
        dropdown_html = f'''
            <div class="section-nav-dropdown">
                <button onclick="toggleDropdown('{dropdown_id}')" class="dropdown-btn">
                    Quick Nav ▼
                </button>
                <div id="{dropdown_id}" class="dropdown-content">
        '''
        
        # Add links to all sections in this category
        for move_type in category_info['moves']:
            if move_type == 'fighter_stats':
                continue  # Skip fighter stats in other categories
                
            move_name = category_info['move_names'][move_type]
            section_id = f"section_{move_type}"
            
            # Mark current section
            current_class = ' class="current-section"' if move_type == current_move else ''
            
            dropdown_html += f'''
                    <a href="#{section_id}" onclick="scrollToSection('{section_id}'); toggleDropdown('{dropdown_id}')" {current_class}>
                        {move_name}
                    </a>
            '''
        
        dropdown_html += '''
                </div>
            </div>
        '''
        return dropdown_html
    
    move_categories = {
        'fighter_stats': {
            'title': 'Fighter Stats',
            'moves': ['fighter_stats'],
            'move_names': {
                'fighter_stats': 'Fighter Statistics'
            },
            'filename': 'fighter_stats.html'
        },
        'jabs': {
            'title': 'Jab Attacks',
            'moves': ['jab1', 'jab2', 'jab3'],
            'move_names': {
                'jab1': 'Jab 1', 'jab2': 'Jab 2', 'jab3': 'Jab 3',
            },
            'filename': 'jabs_attacks.html'
        },
        'tilts': {
            'title': 'Tilt Attacks',
            'moves': ['ftilt', 'utilt', 'dtilt'],
            'move_names': {
                'ftilt': 'Forward Tilt', 'utilt': 'Up Tilt', 'dtilt': 'Down Tilt'
            },
            'filename': 'tilts_attacks.html'
        },
        'smashes': {
            'title': 'Smash Attacks',
            'moves': ['fsmash', 'usmash', 'dsmash'],
            'move_names': {
                'fsmash': 'Forward Smash', 'usmash': 'Up Smash', 'dsmash': 'Down Smash'
            },
            'filename': 'smashes_attacks.html'
        },
        'aerials': {
            'title': 'Aerial Attacks',
            'moves': ['nair', 'fair', 'bair', 'uair', 'dair'],
            'move_names': {
                'nair': 'Neutral Air', 'fair': 'Forward Air', 'bair': 'Back Air', 'uair': 'Up Air', 'dair': 'Down Air'
            },
            'filename': 'aerials_attacks.html'
        },
        'dash': {
            'title': 'Dash Attack',
            'moves': ['dash_attack'],
            'move_names': {
                'dash_attack': 'Dash Attack'
            },
            'filename': 'dash_attacks.html'
        },
        'grabs': {
            'title': 'Grabs & Throws',
            'moves': ['grab', 'dash_grab', 'pivot_grab', 'pummel', 'fthrow', 'bthrow', 'uthrow', 'dthrow'],
            'move_names': {
                'grab': 'Grab', 'dash_grab': 'Dash Grab', 'pivot_grab': 'Pivot Grab',
                'pummel': 'Pummel', 'fthrow': 'Forward Throw', 'bthrow': 'Back Throw', 
                'uthrow': 'Up Throw', 'dthrow': 'Down Throw'
            },
            'filename': 'grabs_attacks.html'
        },
        'specials': {
            'title': 'Special Attacks',
            'moves': ['neutral_b', 'side_b', 'up_b', 'down_b', 'neutral_b_air', 'side_b_air', 'up_b_air', 'down_b_air'],
            'move_names': {
                'neutral_b': 'Neutral Special', 'side_b': 'Side Special', 'up_b': 'Up Special', 'down_b': 'Down Special',
                'neutral_b_air': 'Neutral Special (Air)', 'side_b_air': 'Side Special (Air)', 'up_b_air': 'Up Special (Air)', 'down_b_air': 'Down Special (Air)'
            },
            'filename': 'specials_attacks.html'
        }
    }
    
    output_dir = "output_html"
    os.makedirs(output_dir, exist_ok=True)

    # Generate category-specific HTML files
    for category_key, category_info in move_categories.items():
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category_info['title']} - Attack Data</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .return-button {{
            display: inline-block;
            margin-bottom: 20px;
            padding: 10px 15px;
            background-color: #6c757d;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s;
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 1000;
        }}
        .return-button:hover {{
            background-color: #5a6268;
        }}
        h1 {{
            color: #333;
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #007bff;
            padding-left: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background-color: white;
            font-size: 0.9em;
        }}
        th {{
            background-color: #007bff;
            color: white;
            padding: 10px 8px;
            text-align: left;
            font-weight: bold;
            cursor: pointer;
        }}
        th:hover {{
            background-color: #0056b3;
        }}
        th.sortable {{
            position: relative;
            padding-right: 25px;
        }}
        th.sortable .sort-icon {{
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.8em;
            color: #fff;
            opacity: 0.6;
        }}
        th.sortable:hover .sort-icon {{
            opacity: 1;
        }}
        td {{
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e3f2fd;
        }}
        .damage {{
            font-weight: bold;
            color: #d32f2f;
        }}
        .frame {{
            font-weight: bold;
            color: #388e3c;
        }}
        .value {{
            font-weight: bold;
            color: #0056b3;
        }}
        .not-found {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 15px;
            margin-top: 20px;
        }}
        .not-found h3 {{
            color: #856404;
            margin-top: 0;
        }}
        .not-found-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 5px;
            margin-top: 10px;
        }}
        .fallback-info {{
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 4px;
            padding: 15px;
            margin-top: 20px;
        }}
        .fallback-info h3 {{
            color: #0c5460;
            margin-top: 0;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
            border-top: 1px solid #ddd;
            padding-top: 10px;
        }}
        .shield-advantage-positive {{
            font-weight: bold;
            color: #2e7d32;  /* Green for positive advantage (safe on shield) */
        }}
        .shield-advantage-negative {{
            font-weight: bold;
            color: #d32f2f;  /* Red for negative advantage (punishable) */
        }}
        .shield-advantage-neutral {{
            font-weight: bold;
            color: #f57c00;  /* Orange for neutral/small advantage */
        }}
        
        /* Tooltip styles */
        .tooltip {{
            position: relative;
            cursor: help;
        }}
        .tooltip .tooltip-content {{
            visibility: hidden;
            opacity: 0;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background-color: #333;
            color: white;
            text-align: left;
            padding: 10px;
            border-radius: 6px;
            font-size: 0.85em;
            line-height: 1.4;
            white-space: nowrap;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            transition: opacity 0.3s, visibility 0.3s;
            max-width: 300px;
            white-space: normal;
        }}
        .tooltip .tooltip-content::after {{
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #333 transparent transparent transparent;
        }}
        .tooltip:hover .tooltip-content {{
            visibility: visible;
            opacity: 1;
        }}
        .has-tooltip {{
            background-color: #fff3e0 !important;
        }}
        .has-tooltip:hover {{
            background-color: #ffe0b2 !important;
        }}
        .info-icon {{
            display: inline-block;
            width: 16px;
            height: 16px;
            background-color: #007bff;
            color: white;
            border-radius: 50%;
            text-align: center;
            font-size: 12px;
            line-height: 16px;
            margin-left: 5px;
            cursor: help;
            font-weight: bold;
        }}

        .info-icon:hover {{
            background-color: #0056b3;
        }}

        .section-header {{
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .section-nav-dropdown {{
            position: relative;
            display: inline-block;
            margin-left: 15px;
        }}
        .dropdown-btn {{
            background-color: #FF8400;
            color: white;
            padding: 8px 12px;
            font-size: 14px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .dropdown-btn:hover {{
            background-color: #D6812D;
        }}
        .dropdown-content {{
            display: none;
            position: absolute;
            right: 0;
            background-color: #f9f9f9;
            min-width: 200px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
            border-radius: 4px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .dropdown-content a {{
            color: black;
            padding: 12px 16px;
            text-decoration: none;
            display: block;
            transition: background-color 0.3s;
        }}
        .dropdown-content a:hover {{
            background-color: #f1f1f1;
        }}
        .dropdown-content a.current-section {{
            background-color: #e3f2fd;
            font-weight: bold;
        }}
        .show {{
            display: block;
        }}
        /* Specific styling for tooltips in table headers - position below */
        th.tooltip .tooltip-content {{
            bottom: auto;
            top: 125%;
        }}

        th.tooltip .tooltip-content::after {{
            content: "";
            position: absolute;
            bottom: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: transparent transparent #333 transparent;
        }}
    </style>
    <script>
        function sortTable(tableId, n) {{
            var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            table = document.getElementById(tableId);
            switching = true;
            dir = "asc";
            while (switching) {{
                switching = false;
                rows = table.rows;
                for (i = 1; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i + 1].getElementsByTagName("TD")[n];
                    var xContent = x.innerHTML.replace(/<[^>]*>/g, "").trim();
                    var yContent = y.innerHTML.replace(/<[^>]*>/g, "").trim();

                    var xValue = parseFloat(xContent);
                    var yValue = parseFloat(yContent);

                    var isNumericComparison = !isNaN(xValue) && !isNaN(yValue) && 
                                              xContent !== "N/A" && yContent !== "N/A";

                    if (dir == "asc") {{
                        if (isNumericComparison) {{
                            if (xValue > yValue) {{
                                shouldSwitch = true;
                                break;
                            }}
                        }} else {{
                            if (xContent.toLowerCase() > yContent.toLowerCase()) {{
                                shouldSwitch = true;
                                break;
                            }}
                        }}
                    }} else if (dir == "desc") {{
                        if (isNumericComparison) {{
                            if (xValue < yValue) {{
                                shouldSwitch = true;
                                break;
                            }}
                        }} else {{
                            if (xContent.toLowerCase() < yContent.toLowerCase()) {{
                                shouldSwitch = true;
                                break;
                            }}
                        }}
                    }}
                }}
                if (shouldSwitch) {{
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount ++;
                }} else {{
                    if (switchcount == 0 && dir == "asc") {{
                        dir = "desc";
                        switching = true;
                    }}
                }}
            }}
        }}
        
        /* NEW: Dropdown functionality */
        function toggleDropdown(dropdownId) {{
            document.getElementById(dropdownId).classList.toggle("show");
        }}

        // Close dropdowns when clicking outside
        window.onclick = function(event) {{
            if (!event.target.matches('.dropdown-btn')) {{
                var dropdowns = document.getElementsByClassName("dropdown-content");
                for (var i = 0; i < dropdowns.length; i++) {{
                    var openDropdown = dropdowns[i];
                    if (openDropdown.classList.contains('show')) {{
                        openDropdown.classList.remove('show');
                    }}
                }}
            }}
        }}

        // Smooth scrolling for section links
        function scrollToSection(sectionId) {{
            document.getElementById(sectionId).scrollIntoView({{
                behavior: 'smooth',
                block: 'start'
            }});
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            var tables = document.querySelectorAll('table');
            tables.forEach(function(table) {{
                var ths = table.querySelectorAll('th');
                ths.forEach(function(th, index) {{
                    th.addEventListener('click', function() {{
                        sortTable(table.id, index);
                    }});
                }});
                if (!table.id) {{
                    table.id = 'sortableTable_' + Math.random().toString(36).substr(2, 9);
                }}
            }});
        }});
    </script>
</head>
<body>
    <a href="index.html" class="return-button">Return to Index</a>
    <div class="container">
        <h1>{category_info['title']}</h1>
        <p style="text-align: center; color: #666;">Attack damage, knockback, and frame data analysis</p>
"""

        for move_type in category_info['moves']:
            # Special handling for grab moves - create a combined table
            if move_type in ['grab', 'dash_grab', 'pivot_grab']:
                if move_type == 'grab':  # Only create table once, on first grab move
                    section_id = "section_grabs"
                    # Create a special category info for grabs dropdown
                    grab_category_info = {
                        'moves': ['grab', 'pummel', 'fthrow', 'bthrow', 'uthrow', 'dthrow'],
                        'move_names': {
                            'grab': 'Grabs', 'pummel': 'Pummel', 'fthrow': 'Forward Throw', 
                            'bthrow': 'Back Throw', 'uthrow': 'Up Throw', 'dthrow': 'Down Throw'
                        }
                    }
                    dropdown_html = generate_section_dropdown('grab', grab_category_info)
                    html_content += f"""
        <h2 id="{section_id}" class="section-header">
            <span>Grabs</span>
            {dropdown_html}
        </h2>
        """
                    # Collect all grab data for each character
                    grab_data = {}
                    for grab_type in ['grab', 'dash_grab', 'pivot_grab']:
                        if results[grab_type]:
                            for char_data in results[grab_type]:
                                char_name = char_data[0]
                                if char_name not in grab_data:
                                    grab_data[char_name] = {'grab': 'N/A', 'dash_grab': 'N/A', 'pivot_grab': 'N/A'}
                                grab_data[char_name][grab_type] = char_data[3] if char_data[3] else 'N/A'  # Frame is at index 3
                    
                    if grab_data:
                        html_content += """
                <table id="grabs_table">
                    <thead>
                        <tr>
                            <th class="sortable">Character <span class="sort-icon">&#x2195;</span></th>
                            <th class="sortable">Grab Frame <span class="sort-icon">&#x2195;</span></th>
                            <th class="sortable">Dash Grab Frame <span class="sort-icon">&#x2195;</span></th>
                            <th class="sortable">Pivot Grab Frame <span class="sort-icon">&#x2195;</span></th>
                        </tr>
                    </thead>
                    <tbody>
        """
                        # Generate rows
                        for char_name in sorted(grab_data.keys()):
                            html_content += f"""
                        <tr>
                            <td>{char_name}</td>
                            <td class="frame">{grab_data[char_name]['grab']}</td>
                            <td class="frame">{grab_data[char_name]['dash_grab']}</td>
                            <td class="frame">{grab_data[char_name]['pivot_grab']}</td>
                        </tr>
        """
                        
                        html_content += """
                    </tbody>
                </table>
        """
                    else:
                        html_content += """
                <p><em>No grab data found.</em></p>
        """
                continue  # Skip the regular table generation for all grab moves

            # Special handling for fighter stats
            if move_type == 'fighter_stats':
                section_id = "section_fighter_stats"
                html_content += f"""
        <h2 id="{section_id}">Movement & Physics Stats</h2>
        """
                
                if fighter_stats_data:
                    sorted_stats = sorted(fighter_stats_data.items(), key=lambda x: x[0].lower())
                    
                    html_content += """
        <table id="fighter_stats_table">
            <thead>
                <tr>
                    <th class="sortable">Character <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Walk Speed <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Run Speed <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Dash Speed <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Air Acceleration <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Max Horizontal Air Speed <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Weight <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Ground-to-air Momentum <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Fall Speed <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Gravity <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Full Hop Height <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Short Hop Height <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Double Jump Height <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Jumpsquat <span class="sort-icon">&#x2195;</span></th>
                </tr>
            </thead>
            <tbody>
"""
                    
                    # Format each stat value, handling None values
                    def format_stat(value, decimal_places=3):
                        if value is None:
                            return "N/A"
                        if isinstance(value, int):
                            return str(value)
                        if decimal_places == 0:
                            # For integers (like weight), don't strip zeros
                            return f"{value:.0f}"
                        else:
                            # For decimals, strip trailing zeros and decimal point
                            return f"{value:.{decimal_places}f}".rstrip('0').rstrip('.')
                    
                    for char_name, stats in sorted_stats:
                        walk_speed = format_stat(stats.get('walk_speed'))
                        run_speed = format_stat(stats.get('run_speed'))
                        dash_speed = format_stat(stats.get('dash_speed'))
                        air_acceleration = format_stat(stats.get('air_acceleration'))     # NEW - moved here
                        max_air_speed = format_stat(stats.get('max_air_speed'))           # NEW - moved here
                        weight = format_stat(stats.get('weight'), 0)
                        jump_speed_x_max = format_stat(stats.get('jump_speed_x_max'))
                        fall_speed = format_stat(stats.get('fall_speed'))
                        gravity = format_stat(stats.get('gravity')) 
                        full_hop = format_stat(stats.get('full_hop'))
                        short_hop = format_stat(stats.get('short_hop'))
                        double_jump = format_stat(stats.get('double_jump'))
                        jumpsquat = format_stat(stats.get('jumpsquat'), 0)
                        
                        html_content += f"""
                        <tr>
                            <td>{char_name}</td>
                            <td class="value">{walk_speed}</td>
                            <td class="value">{run_speed}</td>
                            <td class="value">{dash_speed}</td>
                            <td class="value">{air_acceleration}</td>
                            <td class="value">{max_air_speed}</td>
                            <td class="value">{weight}</td>
                            <td class="value">{jump_speed_x_max}</td>
                            <td class="value">{fall_speed}</td>
                            <td class="value">{gravity}</td>
                            <td class="value">{full_hop}</td>
                            <td class="value">{short_hop}</td>
                            <td class="value">{double_jump}</td>
                            <td class="frame">{jumpsquat}</td>
                        </tr>"""
                    
                    html_content += """
            </tbody>
        </table>
        """
                else:
                    html_content += """
        <p><em>No fighter stats data found.</em></p>
        """
                
                continue  # Skip the regular processing for fighter stats
            
            # Regular table generation for non-grab moves
            move_name = category_info['move_names'][move_type]
            section_id = f"section_{move_type}"

            # Only add dropdown for multi-section pages
            if move_type == 'dash_attack':
                html_content += f"""
                    <h2 id="{section_id}">{move_name}</h2>
            """
            else:
                dropdown_html = generate_section_dropdown(move_type, category_info)
                html_content += f"""
                    <h2 id="{section_id}" class="section-header">
                        <span>{move_name}</span>
                        {dropdown_html}
                    </h2>
            """
            
            if results[move_type]:
                sorted_results = sorted(results[move_type], key=lambda x: x[0].lower())
                
                # Check if this is an aerial move that should show landing lag and shield advantage
                is_aerial = move_type in ['nair', 'fair', 'bair', 'uair', 'dair']
                
                table_id = f"{move_type}_table"
                html_content += f"""
        <table id="{table_id}">
            <thead>
                <tr>
                    <th class="sortable">Character <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Damage <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Angle <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">KBG <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">FKB <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">BKB <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">Frame <span class="sort-icon">&#x2195;</span></th>
                    <th class="sortable">FAF <span class="sort-icon">&#x2195;</span></th>"""
                
                # Add landing lag and shield advantage columns only for aerials
                if is_aerial:
                    html_content += """
                                    <th class="sortable">Landing Lag <span class="sort-icon">&#x2195;</span></th>
                                    <th class="sortable tooltip">Optimal Shield Advantage <span class="info-icon">?</span> <span class="sort-icon">&#x2195;</span>
                                        <div class="tooltip-content">Optimal Shield Advantage is calculated assuming you are landing while using the move, entering landing lag on the first possible frame after the moves hitbox comes out. Using aerials in other contexts, such as rising on shield and letting the full animation complete, is not accounted for here and cannot be calculated algorithmically at this time.</div>
                                    </th>"""
                
                html_content += """
                </tr>
            </thead>
            <tbody>
"""
                
                for char_data in sorted_results:
                    display_name = char_data[0]
                    final_damage = char_data[1]  # Actual numeric damage value
                    display_damage = char_data[2]
                    frame_display = char_data[3]
                    display_angle = char_data[5]
                    display_kbg = char_data[7]
                    display_fkb = char_data[9]
                    display_bkb = char_data[11]
                    faf_display = char_data[14] if len(char_data) > 14 else "N/A"
                    
                    # Check if this character needs a tooltip
                    tooltip_content = generate_tooltip_content(display_name, move_type, char_data)
                    tooltip_class = " has-tooltip" if tooltip_content else ""
                    tooltip_html = ""
                    
                    if tooltip_content:
                        tooltip_html = f"""<div class="tooltip-content">{tooltip_content}</div>"""
                    
                    html_content += f"""
                <tr class="tooltip{tooltip_class}">
                    <td>{display_name}{tooltip_html}</td>
                    <td class="damage">{display_damage}</td>
                    <td class="value">{display_angle}</td>
                    <td class="value">{display_kbg}</td>
                    <td class="value">{display_fkb}</td>
                    <td class="value">{display_bkb}</td>
                    <td class="frame">{frame_display}</td>
                    <td class="frame">{faf_display}</td>"""
                    
                    # Add landing lag and shield advantage cells only for aerials
                    if is_aerial:
                        # Extract landing lag from tuple (13th element for aerials)
                        landing_lag = char_data[12] if len(char_data) > 12 else 0
                        
                        # Calculate optimal shield advantage: (Damage * 0.55) + 2 - Lag
                        if final_damage is not None and final_damage > 0:
                            shield_advantage = (final_damage * 0.55) + 2 - landing_lag
                            # Round down (floor) to match in-game behavior
                            shield_advantage_floored = math.floor(shield_advantage)
                            shield_advantage_display = str(shield_advantage_floored)
                            
                            # Add color coding based on advantage
                            if shield_advantage_floored > 0:
                                shield_class = "shield-advantage-positive"
                            elif shield_advantage_floored < -2:
                                shield_class = "shield-advantage-negative"
                            else:
                                shield_class = "shield-advantage-neutral"
                        else:
                            shield_advantage_display = "N/A"
                            shield_class = "value"
                        
                        html_content += f"""
                    <td class="frame">{landing_lag}</td>
                    <td class="{shield_class}">{shield_advantage_display}</td>"""
                    
                    html_content += """
                </tr>
"""
                
                html_content += """
            </tbody>
        </table>
"""
                
                # NOTE: Removed the explanatory sections - they're now tooltips!
                    
            else:
                html_content += """
        <p><em>No data found for this move.</em></p>
"""
            
            if not_found[move_type]:
                sorted_not_found = sorted(not_found[move_type])
                html_content += f"""
        <div class="not-found">
            <h3>Characters Not Found ({len(sorted_not_found)})</h3>
            <div class="not-found-list">
"""
                for name in sorted_not_found:
                    html_content += f"                <div>{name}</div>\n"

                html_content += """
            </div>
        </div>
"""
            
            if fallback_found[move_type]:
                sorted_fallback = sorted(fallback_found[move_type])
                html_content += f"""
        <div class="fallback-info">
            <h3>Characters Found in Fallback Location ({len(sorted_fallback)})</h3>
            <div class="not-found-list">
"""
                for name in sorted_fallback:
                    html_content += f"                <div>{name}</div>\n"
                html_content += """
            </div>
        </div>
"""

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content += f"""
        <div class="timestamp">
            Generated on: {now}
        </div>
    </div>
</body>
</html>
"""
        output_filename = os.path.join(output_dir, category_info['filename'])
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Generated {output_filename}")


if __name__ == "__main__":
    print("Starting attack data analysis...")
    all_results, all_not_found, all_fallback_found, landing_lag_data, fighter_stats_data = find_all_attacks()
    print("Analysis complete. Generating HTML files...")
    generate_html_files(all_results, all_not_found, all_fallback_found, fighter_stats_data)
    print("HTML files generated successfully in 'output_html' directory.")