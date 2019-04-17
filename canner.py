#!/usr/bin/python3
# this script should be placed in your minecraft directory
import time
import re
from os.path import getmtime, sep, abspath, dirname
from os import walk, getcwd, mkdir, scandir, unlink
from hashlib import sha1
from base64 import b64encode
cwd = getcwd()
# regex used in multiple functions
code_rd = re.compile(r'((?:.*,\n)*.*?)\s*:(\n(\s*)[^\n]*(?:\n[^\n\S]+[^\n]*)*)|(.+)')
# regex used in function 'on_modified'
commrmv = re.compile(r'\s*(?:#|\/\/).*|\/\*[\s\S]*\*\/')
# regex used in function 'code_parse'
blckfor = re.compile(r'^for\s+((?:\S+,\s*)*\S+)\s+in\s+(?:((?:\S+,\s*)*\S+)|(-?\d+)\s+to\s+(-?\d+))$')
blckexc = re.compile(r'^execute\s+(while(\s+not))?.*\s+run$')
whleclc = re.compile(r'^(execute\s+)while(\s+not\s+)?(block\s+(?:[~^]?-?\d*\s+){3}\S+|blocks\s+(?:[~^]?-?\d*\s+){9}\S+|entity\s+\S+|score(?:\s+\S+){2}(?:\s+[<>=]{1,2})?(?:\s+\S+){2})\s+(.*)run$')
# regex unused
# cmdsepr = re.compile(r'(?:[^\n](?:\\.)?)+')
# rngeclc = re.compile(r'range\s+(-?\d+),\s*(-?\d+)')
# regex used in function 'export_mcfunction'
fncpref = re.compile(r'(function[^\S\n]+)([^:\s]+\s)')
spcefix = re.compile(r'\n\s+')
whlecvt = re.compile(r'execute if not')
exctexp = re.compile(r'execute\s+(@[^\n]*?)(\s+(?:align|anchored|as|at|facing|if|in|positioned|rotated|run|store|unless))')

lastmod = {}
b62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
invsize = {'hopper':{'Items':5},'furnace':{'Items':3},'chest, shulker_box':{'Items':9*3},'player':{'Inventory':(9*4)+5},'dispenser, dropper':{'Items':3*3},'default':{'ArmorItems':4,'HandItems':2},
'items':['stone','granite','polished_granite','diorite','polished_diorite','andesite','polished_andesite','grass_block','dirt','coarse_dirt','podzol','cobblestone','oak_planks','spruce_planks','birch_planks','jungle_planks','acacia_planks','dark_oak_planks','oak_sapling','spruce_sapling','birch_sapling','jungle_sapling','acacia_sapling','dark_oak_sapling','bedrock','sand','red_sand','gravel','gold_ore','iron_ore','coal_ore','oak_log','spruce_log','birch_log','jungle_log','acacia_log','dark_oak_log','stripped_oak_log','stripped_spruce_log','stripped_birch_log','stripped_jungle_log','stripped_acacia_log','stripped_dark_oak_log','stripped_oak_wood','stripped_spruce_wood','stripped_birch_wood','stripped_jungle_wood','stripped_acacia_wood','stripped_dark_oak_wood','oak_wood','spruce_wood','birch_wood','jungle_wood','acacia_wood','dark_oak_wood','oak_leaves','spruce_leaves','birch_leaves','jungle_leaves','acacia_leaves','dark_oak_leaves','sponge','wet_sponge','glass','lapis_ore','lapis_block','dispenser','sandstone','chiseled_sandstone','cut_sandstone','note_block','powered_rail','detector_rail','sticky_piston','cobweb','grass','fern','dead_bush','seagrass','sea_pickle','piston','white_wool','orange_wool','magenta_wool','light_blue_wool','yellow_wool','lime_wool','pink_wool','gray_wool','light_gray_wool','cyan_wool','purple_wool','blue_wool','brown_wool','green_wool','red_wool','black_wool','dandelion','poppy','blue_orchid','allium','azure_bluet','red_tulip','orange_tulip','white_tulip','pink_tulip','oxeye_daisy','brown_mushroom','red_mushroom','gold_block','iron_block','oak_slab','spruce_slab','birch_slab','jungle_slab','acacia_slab','dark_oak_slab','stone_slab','sandstone_slab','petrified_oak_slab','cobblestone_slab','brick_slab','stone_brick_slab','nether_brick_slab','quartz_slab','red_sandstone_slab','purpur_slab','prismarine_slab','prismarine_brick_slab','dark_prismarine_slab','smooth_quartz','smooth_red_sandstone','smooth_sandstone','smooth_stone','bricks','tnt','bookshelf','mossy_cobblestone','obsidian','torch','end_rod','chorus_plant','chorus_flower','purpur_block','purpur_pillar','purpur_stairs','spawner','oak_stairs','chest','diamond_ore','diamond_block','crafting_table','farmland','furnace','ladder','rail','cobblestone_stairs','lever','stone_pressure_plate','oak_pressure_plate','spruce_pressure_plate','birch_pressure_plate','jungle_pressure_plate','acacia_pressure_plate','dark_oak_pressure_plate','redstone_ore','redstone_torch','stone_button','snow','ice','snow_block','cactus','clay','jukebox','oak_fence','spruce_fence','birch_fence','jungle_fence','acacia_fence','dark_oak_fence','pumpkin','carved_pumpkin','netherrack','soul_sand','glowstone','jack_o_lantern','oak_trapdoor','spruce_trapdoor','birch_trapdoor','jungle_trapdoor','acacia_trapdoor','dark_oak_trapdoor','infested_stone','infested_cobblestone','infested_stone_bricks','infested_mossy_stone_bricks','infested_cracked_stone_bricks','infested_chiseled_stone_bricks','stone_bricks','mossy_stone_bricks','cracked_stone_bricks','chiseled_stone_bricks','brown_mushroom_block','red_mushroom_block','mushroom_stem','iron_bars','glass_pane','melon','vine','oak_fence_gate','spruce_fence_gate','birch_fence_gate','jungle_fence_gate','acacia_fence_gate','dark_oak_fence_gate','brick_stairs','stone_brick_stairs','mycelium','lily_pad','nether_bricks','nether_brick_fence','nether_brick_stairs','enchanting_table','end_portal_frame','end_stone','end_stone_bricks','dragon_egg','redstone_lamp','sandstone_stairs','emerald_ore','ender_chest','tripwire_hook','emerald_block','spruce_stairs','birch_stairs','jungle_stairs','command_block','beacon','cobblestone_wall','mossy_cobblestone_wall','oak_button','spruce_button','birch_button','jungle_button','acacia_button','dark_oak_button','anvil','chipped_anvil','damaged_anvil','trapped_chest','light_weighted_pressure_plate','heavy_weighted_pressure_plate','daylight_detector','redstone_block','nether_quartz_ore','hopper','chiseled_quartz_block','quartz_block','quartz_pillar','quartz_stairs','activator_rail','dropper','white_terracotta','orange_terracotta','magenta_terracotta','light_blue_terracotta','yellow_terracotta','lime_terracotta','pink_terracotta','gray_terracotta','light_gray_terracotta','cyan_terracotta','purple_terracotta','blue_terracotta','brown_terracotta','green_terracotta','red_terracotta','black_terracotta','barrier','iron_trapdoor','hay_block','white_carpet','orange_carpet','magenta_carpet','light_blue_carpet','yellow_carpet','lime_carpet','pink_carpet','gray_carpet','light_gray_carpet','cyan_carpet','purple_carpet','blue_carpet','brown_carpet','green_carpet','red_carpet','black_carpet','terracotta','coal_block','packed_ice','acacia_stairs','dark_oak_stairs','slime_block','grass_path','sunflower','lilac','rose_bush','peony','tall_grass','large_fern','white_stained_glass','orange_stained_glass','magenta_stained_glass','light_blue_stained_glass','yellow_stained_glass','lime_stained_glass','pink_stained_glass','gray_stained_glass','light_gray_stained_glass','cyan_stained_glass','purple_stained_glass','blue_stained_glass','brown_stained_glass','green_stained_glass','red_stained_glass','black_stained_glass','white_stained_glass_pane','orange_stained_glass_pane','magenta_stained_glass_pane','light_blue_stained_glass_pane','yellow_stained_glass_pane','lime_stained_glass_pane','pink_stained_glass_pane','gray_stained_glass_pane','light_gray_stained_glass_pane','cyan_stained_glass_pane','purple_stained_glass_pane','blue_stained_glass_pane','brown_stained_glass_pane','green_stained_glass_pane','red_stained_glass_pane','black_stained_glass_pane','prismarine','prismarine_bricks','dark_prismarine','prismarine_stairs','prismarine_brick_stairs','dark_prismarine_stairs','sea_lantern','red_sandstone','chiseled_red_sandstone','cut_red_sandstone','red_sandstone_stairs','repeating_command_block','chain_command_block','magma_block','nether_wart_block','red_nether_bricks','bone_block','structure_void','observer','shulker_box','white_shulker_box','orange_shulker_box','magenta_shulker_box','light_blue_shulker_box','yellow_shulker_box','lime_shulker_box','pink_shulker_box','gray_shulker_box','light_gray_shulker_box','cyan_shulker_box','purple_shulker_box','blue_shulker_box','brown_shulker_box','green_shulker_box','red_shulker_box','black_shulker_box','white_glazed_terracotta','orange_glazed_terracotta','magenta_glazed_terracotta','light_blue_glazed_terracotta','yellow_glazed_terracotta','lime_glazed_terracotta','pink_glazed_terracotta','gray_glazed_terracotta','light_gray_glazed_terracotta','cyan_glazed_terracotta','purple_glazed_terracotta','blue_glazed_terracotta','brown_glazed_terracotta','green_glazed_terracotta','red_glazed_terracotta','black_glazed_terracotta','white_concrete','orange_concrete','magenta_concrete','light_blue_concrete','yellow_concrete','lime_concrete','pink_concrete','gray_concrete','light_gray_concrete','cyan_concrete','purple_concrete','blue_concrete','brown_concrete','green_concrete','red_concrete','black_concrete','white_concrete_powder','orange_concrete_powder','magenta_concrete_powder','light_blue_concrete_powder','yellow_concrete_powder','lime_concrete_powder','pink_concrete_powder','gray_concrete_powder','light_gray_concrete_powder','cyan_concrete_powder','purple_concrete_powder','blue_concrete_powder','brown_concrete_powder','green_concrete_powder','red_concrete_powder','black_concrete_powder','turtle_egg','dead_tube_coral_block','dead_brain_coral_block','dead_bubble_coral_block','dead_fire_coral_block','dead_horn_coral_block','tube_coral_block','brain_coral_block','bubble_coral_block','fire_coral_block','horn_coral_block','tube_coral','brain_coral','bubble_coral','fire_coral','horn_coral','dead_brain_coral','dead_bubble_coral','dead_fire_coral','dead_horn_coral','dead_tube_coral','tube_coral_fan','brain_coral_fan','bubble_coral_fan','fire_coral_fan','horn_coral_fan','dead_tube_coral_fan','dead_brain_coral_fan','dead_bubble_coral_fan','dead_fire_coral_fan','dead_horn_coral_fan','blue_ice','conduit','iron_door','oak_door','spruce_door','birch_door','jungle_door','acacia_door','dark_oak_door','repeater','comparator','structure_block','turtle_helmet','scute','iron_shovel','iron_pickaxe','iron_axe','flint_and_steel','apple','bow','arrow','coal','charcoal','diamond','iron_ingot','gold_ingot','iron_sword','wooden_sword','wooden_shovel','wooden_pickaxe','wooden_axe','stone_sword','stone_shovel','stone_pickaxe','stone_axe','diamond_sword','diamond_shovel','diamond_pickaxe','diamond_axe','stick','bowl','mushroom_stew','golden_sword','golden_shovel','golden_pickaxe','golden_axe','string','feather','gunpowder','wooden_hoe','stone_hoe','iron_hoe','diamond_hoe','golden_hoe','wheat_seeds','wheat','bread','leather_helmet','leather_chestplate','leather_leggings','leather_boots','chainmail_helmet','chainmail_chestplate','chainmail_leggings','chainmail_boots','iron_helmet','iron_chestplate','iron_leggings','iron_boots','diamond_helmet','diamond_chestplate','diamond_leggings','diamond_boots','golden_helmet','golden_chestplate','golden_leggings','golden_boots','flint','porkchop','cooked_porkchop','painting','golden_apple','enchanted_golden_apple','sign','bucket','water_bucket','lava_bucket','minecart','saddle','redstone','snowball','oak_boat','leather','milk_bucket','pufferfish_bucket','salmon_bucket','cod_bucket','tropical_fish_bucket','brick','clay_ball','sugar_cane','kelp','dried_kelp_block','paper','book','slime_ball','chest_minecart','furnace_minecart','egg','compass','fishing_rod','clock','glowstone_dust','cod','salmon','tropical_fish','pufferfish','cooked_cod','cooked_salmon','ink_sac','rose_red','cactus_green','cocoa_beans','lapis_lazuli','purple_dye','cyan_dye','light_gray_dye','gray_dye','pink_dye','lime_dye','dandelion_yellow','light_blue_dye','magenta_dye','orange_dye','bone_meal','bone','sugar','cake','white_bed','orange_bed','magenta_bed','light_blue_bed','yellow_bed','lime_bed','pink_bed','gray_bed','light_gray_bed','cyan_bed','purple_bed','blue_bed','brown_bed','green_bed','red_bed','black_bed','cookie','filled_map','shears','melon_slice','dried_kelp','pumpkin_seeds','melon_seeds','beef','cooked_beef','chicken','cooked_chicken','rotten_flesh','ender_pearl','blaze_rod','ghast_tear','gold_nugget','nether_wart','potion','splash_potion','lingering_potion','glass_bottle','spider_eye','fermented_spider_eye','blaze_powder','magma_cream','brewing_stand','cauldron','ender_eye','glistering_melon_slice','bat_spawn_egg','blaze_spawn_egg','cave_spider_spawn_egg','chicken_spawn_egg','cod_spawn_egg','cow_spawn_egg','creeper_spawn_egg','dolphin_spawn_egg','donkey_spawn_egg','drowned_spawn_egg','elder_guardian_spawn_egg','enderman_spawn_egg','endermite_spawn_egg','evoker_spawn_egg','ghast_spawn_egg','guardian_spawn_egg','horse_spawn_egg','husk_spawn_egg','llama_spawn_egg','magma_cube_spawn_egg','mooshroom_spawn_egg','mule_spawn_egg','ocelot_spawn_egg','parrot_spawn_egg','phantom_spawn_egg','pig_spawn_egg','polar_bear_spawn_egg','pufferfish_spawn_egg','rabbit_spawn_egg','salmon_spawn_egg','sheep_spawn_egg','shulker_spawn_egg','silverfish_spawn_egg','skeleton_spawn_egg','skeleton_horse_spawn_egg','slime_spawn_egg','spider_spawn_egg','squid_spawn_egg','stray_spawn_egg','tropical_fish_spawn_egg','turtle_spawn_egg','vex_spawn_egg','villager_spawn_egg','vindicator_spawn_egg','witch_spawn_egg','wither_skeleton_spawn_egg','wolf_spawn_egg','zombie_spawn_egg','zombie_horse_spawn_egg','zombie_pigman_spawn_egg','zombie_villager_spawn_egg','experience_bottle','fire_charge','writable_book','written_book','emerald','item_frame','flower_pot','carrot','potato','baked_potato','poisonous_potato','map','golden_carrot','skeleton_skull','wither_skeleton_skull','player_head','zombie_head','creeper_head','dragon_head','carrot_on_a_stick','nether_star','pumpkin_pie','firework_rocket','firework_star','enchanted_book','nether_brick','quartz','tnt_minecart','hopper_minecart','prismarine_shard','prismarine_crystals','rabbit','cooked_rabbit','rabbit_stew','rabbit_foot','rabbit_hide','armor_stand','iron_horse_armor','golden_horse_armor','diamond_horse_armor','lead','name_tag','command_block_minecart','mutton','cooked_mutton','white_banner','orange_banner','magenta_banner','light_blue_banner','yellow_banner','lime_banner','pink_banner','gray_banner','light_gray_banner','cyan_banner','purple_banner','blue_banner','brown_banner','green_banner','red_banner','black_banner','end_crystal','chorus_fruit','popped_chorus_fruit','beetroot','beetroot_seeds','beetroot_soup','dragon_breath','spectral_arrow','tipped_arrow','shield','elytra','spruce_boat','birch_boat','jungle_boat','acacia_boat','dark_oak_boat','totem_of_undying','shulker_shell','iron_nugget','knowledge_book','debug_stick','music_disc_13','music_disc_cat','music_disc_blocks','music_disc_chirp','music_disc_far','music_disc_mall','music_disc_mellohi','music_disc_stal','music_disc_strad','music_disc_ward','music_disc_11','music_disc_wait','trident','phantom_membrane','nautilus_shell'],
'colors':['white','orange','magenta','light_blue','yellow','lime','pink','gray','light_gray','cyan','purple','blue','brown','green','red','black']}
def export_mcfunction(text, filename=False, cmdpref=''):
    text = fncpref.sub(r'\1'+flpt[3]+r':\2', text) # replace "function <funcname>" with "function prefix:<funcname>" (shortcut)
    text = spcefix.sub(r'\n', text).strip() # remove unneeded newlines (code cleanup)
    text = whlecvt.sub(r'execute unless', text) # replace "if not" to "unless" (syntax used in while loop)
    text = exctexp.sub(r'execute as \1 at @s rotated as @s\2', text) # replace "execute @<>" with "execute as @<> at @s rotated as @s" (shortcut)
    if '\n' in text: # export to function
        if not filename:
            hsh = gethash(text)
            filename = bsnm+sep+hsh+func_ext
        else:
            hsh = filename.split(sep)[-1]
            filename = filename+func_ext
        # print(f'==={filename}\n{text}\n==========')
        print(f'writing file {filename}')
        open(filename, 'w').write(f'# this is from a {script_ext} script\n'+text)
        return(f'function {flpt[5]}/{hsh}')
    else: # return single-line
        print(cmdpref+text)
        return(cmdpref+text)
def gethash(text):
    return(re.sub(r'\W',r'',b64encode(sha1(str.encode(text)).digest()).decode())[:10].lower())
def getkey(dict, key):
    for x in dict:
        if key.lower() in x.lower():
            return(x)
    return(False)
def code_parse(code):
    # blockheader, blockbody, blockind, normcmd = code
    # print(f'code: {code}')
    ind = len(code[2])
    if ind == 0 and code[3] != '': # one line
        return(code[3])
    elif ind > 0 and code[3] == '': # code block
        # recursive find codeblocks
        aaa = re.sub(r'\n\s{'+str(ind)+r'}', r'\n', code[1]) # remove whitespace prefix from internal codeblock
        cmds = list(map(code_parse, code_rd.findall(aaa))) # parse commands inside of codeblock
        # print(f'code: {code}')
        ret = ''
        if code[0].startswith('execute'): # execute block
            match = blckexc.match(code[0])
            for cmd in cmds:
                ret = ret+cmd+'\n'
            if not match: # invalid execute block
                raise ValueError(f'for loop invalid syntax: {match[0]}')
            elif match[1]: # while loop
                pref = whleclc.sub(r'\1\4if\2\3 run', code[0])
                hsh = gethash(ret+pref) # get hash of code body plus for statement
                ret = ret+pref+f' function {flpt[5]}/{hsh}\n'
                # print(f'cmdpref: {code[0]}')
                return(pref+' '+export_mcfunction(ret, bsnm+sep+hsh))
            else:
                return(export_mcfunction(ret, False, code[0]+' '))
        elif code[0].startswith('for'): # for block
            match = blckfor.match(code[0])
            lst = []
            if match[2]: # iterate over variables/strings
                for x in list(map(str.strip, match[2].split(','))):
                    if x.count('.') > 0: # specific slots
                        spl = x.split('.')
                        key1 = getkey(invsize, spl[0].strip())
                        key2 = getkey(invsize[key1], spl[-1].strip())
                        for num in range(invsize[key1][key2]):
                            lst.append(f'{key2}[{num}]')
                    else:
                        key1 = getkey(invsize, x.strip())
                        if key1: # all inventory/armor slots
                            for key2 in invsize[key1]:
                                for num in range(invsize[key1][key2]):
                                    lst.append(f'{key2}[{num}]')
                        else: # key not found in invsize, return key
                            lst.append(x.strip())
            elif match[3] and match[4]: # range of numbers "for $v in 0 to 100"
                lst = lst+list(map(str, range(int(match[3]), int(match[4])+1)))
            else: # invalid for loop
                raise ValueError(f'for loop invalid syntax: {match[0]}')
            # print("\n".join(str(x) for x in lst))
            vrs = list(map(str.strip, match[1].split(',')))
            if len(lst)%len(vrs) != 0:
                raise ValueError(f'distribution problem: {len(lst)}/{len(vrs)} ({lst}/{vrs}) ({len(lst)%len(vrs)} variables are homeless!)')
            for n in range(int(len(lst)/len(vrs))):
                for cmd in cmds:
                    for mlt, v in enumerate(vrs): # do a bunch of maths to replace da variablezs
                        cmd = cmd.replace('$'+v, lst[(n*len(vrs))+mlt])
                    ret = ret+cmd+'\n'
            return(export_mcfunction(ret))
    else:
        raise ValueError(f'indentation not found: {code}')
def on_modified():
    global getcode
    print(flnm, flmd)
    lastmod[flnm] = flmd
    rdtxt = commrmv.sub(r'', open(flnm).read())
    # print(f'======================')
    # print(f'input:\n{rdtxt}')
    # print(f'======================')
    try:
        mkdir(bsnm)
    except FileExistsError:
        pass
    if rmoldfnc:
        for file in scandir(bsnm):
            if file.name.endswith(func_ext):
                with open(file) as f:
                    for line in f:
                        if script_ext in line:
                            unlink(file.path)
                        break
    a=''
    for l in list(map(code_parse, code_rd.findall(rdtxt))):
        a = a+l+'\n'
    export_mcfunction(a, bsnm)

script_ext = '.mccanner'
func_ext = '.mcfunction' # extension of .mcfunction files. (default: .mcfunction)
hash_len = 10 # length of sub-function names. low=high collision chance, high=big filename (default: 10)
rmoldfnc = True # remove old (and unused) functions?
while True:
    for (dirpath, dirnames, filenames) in walk(cwd):
        for file in filenames:
            if file.endswith(script_ext):
                flnm = dirpath+sep+file
                flmd = getmtime(flnm)
                bsnm = flnm[:-len(script_ext)]
                flpt = re.search(r'datapacks.*?$', bsnm)[0].split(sep, 5)
                try:
                    if lastmod[flnm] != flmd:
                        on_modified()
                except KeyError:
                    on_modified()
                    pass
    time.sleep(0.5)