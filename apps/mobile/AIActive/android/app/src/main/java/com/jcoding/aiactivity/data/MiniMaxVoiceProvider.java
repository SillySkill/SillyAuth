package com.jcoding.aiactivity.data;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * MiniMax音色列表提供者
 * 包含从官方API获取的完整系统音色列表
 *
 * API文档: https://platform.minimaxi.com/docs/api-reference/voice-management-get
 * 更新时间: 2026-01-24
 *
 * 音色总数: 303个系统音色
 */
public class MiniMaxVoiceProvider {

    private static List<MiniMaxVoice> allVoices;
    private static List<MiniMaxVoice> cartoonVoices;  // 卡通/动漫声音
    private static Map<String, List<MiniMaxVoice>> voicesByLanguage;

    static {
        allVoices = new ArrayList<>();
        cartoonVoices = new ArrayList<>();
        // 使用 LinkedHashMap 保持语言顺序
        voicesByLanguage = new LinkedHashMap<>();

        // ============ 🎬 卡通/动漫声音（特殊分类） ============
        List<MiniMaxVoice> cartoonVoicesList = new ArrayList<>();

        // 节日卡通
        cartoonVoicesList.add(new MiniMaxVoice("Santa_Claus ", "圣诞老人 🎅", "🎬 卡通/动漫", "节日卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("Grinch", "格林奇 🎄", "🎬 卡通/动漫", "节日卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("Rudolph", "鲁道夫 🦌", "🎬 卡通/动漫", "节日卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("Arnold", "阿诺德 💪", "🎬 卡通/动漫", "节日卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("Charming_Santa", "迷人圣诞老人 🎅", "🎬 卡通/动漫", "节日卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("Charming_Lady", "迷人女士 👸", "🎬 卡通/动漫", "节日卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("Sweet_Girl", "甜心女孩 🍬", "🎬 卡通/动漫", "节日卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("Cute_Elf", "可爱精灵 🧝", "🎬 卡通/动漫", "节日卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("Attractive_Girl", "迷人女孩 ✨", "🎬 卡通/动漫", "节日卡通", true));

        // 动物卡通
        cartoonVoicesList.add(new MiniMaxVoice("cartoon_pig", "卡通猪小琪 🐷", "🎬 卡通/动漫", "动物卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("clever_boy", "聪明男童 👦", "🎬 卡通/动漫", "儿童卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("cute_boy", "可爱男童 👦", "🎬 卡通/动漫", "儿童卡通", true));
        cartoonVoicesList.add(new MiniMaxVoice("lovely_girl", "萌萌女童 👧", "🎬 卡通/动漫", "儿童卡通", true));

        // 机甲/科幻
        cartoonVoicesList.add(new MiniMaxVoice("Robot_Armor", "机械战甲 🤖", "🎬 卡通/动漫", "机甲/科幻", true));

        allVoices.addAll(cartoonVoicesList);
        voicesByLanguage.put("🎬 卡通/动漫", cartoonVoicesList);
        cartoonVoices.addAll(cartoonVoicesList);

        // ============ 中文音色 ============
        List<MiniMaxVoice> chineseVoices = new ArrayList<>();

        // 基础音色（旧格式）
        chineseVoices.add(new MiniMaxVoice("male-qn-qingse", "青涩青年", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("male-qn-jingying", "精英青年", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("male-qn-badao", "霸道青年", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("male-qn-daxuesheng", "大学生", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("female-shaonv", "少女", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("female-yujie", "御姐", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("female-chengshu", "成熟女性", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("female-tianmei", "甜美女性", "中文", "女声"));

        // beta版本
        chineseVoices.add(new MiniMaxVoice("male-qn-qingse-jingpin", "青涩青年-beta", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("male-qn-jingying-jingpin", "精英青年-beta", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("male-qn-badao-jingpin", "霸道青年-beta", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("male-qn-daxuesheng-jingpin", "大学生-beta", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("female-shaonv-jingpin", "少女-beta", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("female-yujie-jingpin", "御姐-beta", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("female-chengshu-jingpin", "成熟女性-beta", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("female-tianmei-jingpin", "甜美女性-beta", "中文", "女声"));

        // 角色声音（旧格式）
        chineseVoices.add(new MiniMaxVoice("bingjiao_didi", "病娇弟弟 🎀", "中文", "角色声音", true));
        chineseVoices.add(new MiniMaxVoice("junlang_nanyou", "俊朗男友 💕", "中文", "角色声音", true));
        chineseVoices.add(new MiniMaxVoice("chunzhen_xuedi", "纯真学弟 📚", "中文", "角色声音", true));
        chineseVoices.add(new MiniMaxVoice("lengdan_xiongzhang", "冷淡学长 ❄️", "中文", "角色声音", true));
        chineseVoices.add(new MiniMaxVoice("badao_shaoye", "霸道少爷 👑", "中文", "角色声音", true));
        chineseVoices.add(new MiniMaxVoice("tianxin_xiaoling", "甜心小玲 🎀", "中文", "角色声音", true));
        chineseVoices.add(new MiniMaxVoice("qiaopi_mengmei", "俏皮萌妹 ✨", "中文", "角色声音", true));
        chineseVoices.add(new MiniMaxVoice("wumei_yujie", "妩媚御姐 💃", "中文", "角色声音", true));
        chineseVoices.add(new MiniMaxVoice("diadia_xuemei", "嗲嗲学妹 🎀", "中文", "角色声音", true));
        chineseVoices.add(new MiniMaxVoice("danya_xuejie", "淡雅学姐 🌸", "中文", "角色声音", true));

        // 新格式中文音色（官方推荐）
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Reliable_Executive", "沉稳高管", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_News_Anchor", "新闻女声", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Mature_Woman", "傲娇御姐", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Unrestrained_Young_Man", "不羁青年", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Arrogant_Miss", "嚣张小姐", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Kind-hearted_Antie", "热心大婶", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_HK_Flight_Attendant", "港普空姐", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Humorous_Elder", "搞笑大爷", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Gentleman", "温润男声", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Warm_Bestie", "温暖闺蜜", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Male_Announcer", "播报男声", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Sweet_Lady", "甜美女声", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Southern_Young_Man", "南方小哥", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Wise_Women", "阅历姐姐", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Gentle_Youth", "温润青年", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Warm_Girl", "温暖少女", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Kind-hearted_Elder", "花甲奶奶", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Cute_Spirit", "憨憨萌兽 🐾", "中文", "卡通", true));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Radio_Host", "电台男主播", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Lyrical_Voice", "抒情男声", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Straightforward_Boy", "率真弟弟", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Sincere_Adult", "真诚青年", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Gentle_Senior", "温柔学姐", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Stubborn_Friend", "嘴硬竹马", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Crisp_Girl", "清脆少女", "中文", "女声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Pure-hearted_Boy", "清澈邻家弟弟", "中文", "男声"));
        chineseVoices.add(new MiniMaxVoice("Chinese (Mandarin)_Soft_Girl", "软软女孩", "中文", "女声"));

        // 添加卡通音色
        for (MiniMaxVoice voice : chineseVoices) {
            if (voice.isCartoon() && !cartoonVoices.contains(voice)) {
                cartoonVoices.add(voice);
            }
        }

        allVoices.addAll(chineseVoices);
        voicesByLanguage.put("中文", chineseVoices);

        // ============ 粤语音色 ============
        List<MiniMaxVoice> cantoneseVoices = new ArrayList<>();
        cantoneseVoices.add(new MiniMaxVoice("Cantonese_ProfessionalHost（F)", "专业女主持", "粤语", "女声"));
        cantoneseVoices.add(new MiniMaxVoice("Cantonese_GentleLady", "温柔女声", "粤语", "女声"));
        cantoneseVoices.add(new MiniMaxVoice("Cantonese_ProfessionalHost（M)", "专业男主持", "粤语", "男声"));
        cantoneseVoices.add(new MiniMaxVoice("Cantonese_PlayfulMan", "活泼男声", "粤语", "男声"));
        cantoneseVoices.add(new MiniMaxVoice("Cantonese_CuteGirl", "可爱女孩", "粤语", "女声"));
        cantoneseVoices.add(new MiniMaxVoice("Cantonese_KindWoman", "善良女声", "粤语", "女声"));

        allVoices.addAll(cantoneseVoices);
        voicesByLanguage.put("粤语", cantoneseVoices);

        // ============ 英文音色 ============
        List<MiniMaxVoice> englishVoices = new ArrayList<>();
        englishVoices.add(new MiniMaxVoice("English_Trustworthy_Man", "Trustworthy Man", "English", "Male"));
        englishVoices.add(new MiniMaxVoice("English_Graceful_Lady", "Graceful Lady", "English", "Female"));
        englishVoices.add(new MiniMaxVoice("English_Aussie_Bloke", "Aussie Bloke 🇦🇺", "English", "Male"));
        englishVoices.add(new MiniMaxVoice("English_Whispering_girl", "Whispering girl (ASMR)", "English", "Female"));
        englishVoices.add(new MiniMaxVoice("English_Diligent_Man", "Diligent Man 🇮🇳", "English", "Male"));
        englishVoices.add(new MiniMaxVoice("English_Gentle-voiced_man", "Gentle-voiced man", "English", "Male"));

        allVoices.addAll(englishVoices);
        voicesByLanguage.put("English", englishVoices);

        // ============ 日文音色 ============
        List<MiniMaxVoice> japaneseVoices = new ArrayList<>();
        japaneseVoices.add(new MiniMaxVoice("Japanese_IntellectualSenior", "知性资深", "日本語", "男性"));
        japaneseVoices.add(new MiniMaxVoice("Japanese_DecisivePrincess", "果断公主 👸", "日本語", "女性", true));
        japaneseVoices.add(new MiniMaxVoice("Japanese_LoyalKnight", "忠诚骑士 ⚔️", "日本語", "男性", true));
        japaneseVoices.add(new MiniMaxVoice("Japanese_DominantMan", "强势男性", "日本語", "男性"));
        japaneseVoices.add(new MiniMaxVoice("Japanese_SeriousCommander", "严肃指挥官", "日本語", "男性", true));
        japaneseVoices.add(new MiniMaxVoice("Japanese_ColdQueen", "冷漠女王 ❄️", "日本語", "女性", true));
        japaneseVoices.add(new MiniMaxVoice("Japanese_DependableWoman", "稳重女性", "日本語", "女性"));
        japaneseVoices.add(new MiniMaxVoice("Japanese_GentleButler", "温柔管家 🎩", "日本語", "男性", true));
        japaneseVoices.add(new MiniMaxVoice("Japanese_KindLady", "善良女士", "日本語", "女性"));
        japaneseVoices.add(new MiniMaxVoice("Japanese_CalmLady", "沉静女士", "日本語", "女性"));
        japaneseVoices.add(new MiniMaxVoice("Japanese_OptimisticYouth", "乐观青年", "日本語", "男性"));
        japaneseVoices.add(new MiniMaxVoice("Japanese_GenerousIzakayaOwner", "大方居酒屋老板 🍶", "日本語", "男性", true));
        japaneseVoices.add(new MiniMaxVoice("Japanese_SportyStudent", "运动学生 ⚽", "日本語", "男性"));
        japaneseVoices.add(new MiniMaxVoice("Japanese_InnocentBoy", "天真男孩", "日本語", "男性"));
        japaneseVoices.add(new MiniMaxVoice("Japanese_GracefulMaiden", "优雅少女", "日本語", "女性"));

        // 添加日文卡通音色
        for (MiniMaxVoice voice : japaneseVoices) {
            if (voice.isCartoon() && !cartoonVoices.contains(voice)) {
                cartoonVoices.add(voice);
            }
        }

        allVoices.addAll(japaneseVoices);
        voicesByLanguage.put("日本語", japaneseVoices);

        // ============ 韩文音色 (47个) ============
        List<MiniMaxVoice> koreanVoices = new ArrayList<>();
        koreanVoices.add(new MiniMaxVoice("Korean_SweetGirl", "Sweet Girl", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_CheerfulBoyfriend", "Cheerful Boyfriend", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_EnchantingSister", "Enchanting Sister", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_ShyGirl", "Shy Girl", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_ReliableSister", "Reliable Sister", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_StrictBoss", "Strict Boss", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_SassyGirl", "Sassy Girl", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_ChildhoodFriendGirl", "Childhood Friend Girl", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_PlayboyCharmer", "Playboy Charmer", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_ElegantPrincess", "Elegant Princess 👸", "한국어", "여성", true));
        koreanVoices.add(new MiniMaxVoice("Korean_BraveFemaleWarrior", "Brave Female Warrior ⚔️", "한국어", "여성", true));
        koreanVoices.add(new MiniMaxVoice("Korean_BraveYouth", "Brave Youth", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_CalmLady", "Calm Lady", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_EnthusiasticTeen", "Enthusiastic Teen", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_SoothingLady", "Soothing Lady", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_IntellectualSenior", "Intellectual Senior", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_LonelyWarrior", "Lonely Warrior", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_MatureLady", "Mature Lady", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_InnocentBoy", "Innocent Boy", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_CharmingSister", "Charming Sister", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_AthleticStudent", "Athletic Student", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_BraveAdventurer", "Brave Adventurer", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_CalmGentleman", "Calm Gentleman", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_WiseElf", "Wise Elf 🧝", "한국어", "여성", true));
        koreanVoices.add(new MiniMaxVoice("Korean_CheerfulCoolJunior", "Cheerful Cool Junior", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_DecisiveQueen", "Decisive Queen 👑", "한국어", "여성", true));
        koreanVoices.add(new MiniMaxVoice("Korean_ColdYoungMan", "Cold Young Man", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_MysteriousGirl", "Mysterious Girl", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_QuirkyGirl", "Quirky Girl", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_ConsiderateSenior", "Considerate Senior", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_CheerfulLittleSister", "Cheerful Little Sister", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_DominantMan", "Dominant Man", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_AirheadedGirl", "Airheaded Girl", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_ReliableYouth", "Reliable Youth", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_FriendlyBigSister", "Friendly Big Sister", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_GentleBoss", "Gentle Boss", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_ColdGirl", "Cold Girl", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_HaughtyLady", "Haughty Lady", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_CharmingElderSister", "Charming Elder Sister", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_IntellectualMan", "Intellectual Man", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_CaringWoman", "Caring Woman", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_WiseTeacher", "Wise Teacher", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_ConfidentBoss", "Confident Boss", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_AthleticGirl", "Athletic Girl", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_PossessiveMan", "Possessive Man", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_GentleWoman", "Gentle Woman", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_CockyGuy", "Cocky Guy", "한국어", "남성"));
        koreanVoices.add(new MiniMaxVoice("Korean_ThoughtfulWoman", "Thoughtful Woman", "한국어", "여성"));
        koreanVoices.add(new MiniMaxVoice("Korean_OptimisticYouth", "Optimistic Youth", "한국어", "남성"));

        allVoices.addAll(koreanVoices);
        voicesByLanguage.put("한국어", koreanVoices);

        // ============ 西班牙文音色 ============
        List<MiniMaxVoice> spanishVoices = new ArrayList<>();
        spanishVoices.add(new MiniMaxVoice("Spanish_SereneWoman", "Serene Woman", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_MaturePartner", "Mature Partner", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_CaptivatingStoryteller", "Captivating Storyteller", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_Narrator", "Narrator", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_WiseScholar", "Wise Scholar", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_Kind-heartedGirl", "Kind-hearted Girl", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_DeterminedManager", "Determined Manager", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_BossyLeader", "Bossy Leader", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_ReservedYoungMan", "Reserved Young Man", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_ConfidentWoman", "Confident Woman", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_ThoughtfulMan", "Thoughtful Man", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_Strong-WilledBoy", "Strong-willed Boy", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_SophisticatedLady", "Sophisticated Lady", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_RationalMan", "Rational Man", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_AnimeCharacter", "Anime Character 🎬", "Español", "Mujer", true));
        spanishVoices.add(new MiniMaxVoice("Spanish_Deep-tonedMan", "Deep-toned Man", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_Fussyhostess", "Fussy Hostess", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_SincereTeen", "Sincere Teen", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_FrankLady", "Frank Lady", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_Comedian", "Comedian", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_Debator", "Debator", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_ToughBoss", "Tough Boss", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_Wiselady", "Wise Lady", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_Steadymentor", "Steady Mentor", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_Jovialman", "Jovial Man", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_SantaClaus", "Santa Claus 🎅", "Español", "Hombre", true));
        spanishVoices.add(new MiniMaxVoice("Spanish_Rudolph", "Rudolph 🦌", "Español", "Hombre", true));
        spanishVoices.add(new MiniMaxVoice("Spanish_Intonategirl", "Intonate Girl", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_Arnold", "Arnold 💪", "Español", "Hombre", true));
        spanishVoices.add(new MiniMaxVoice("Spanish_Ghost", "Ghost 👻", "Español", "Hombre", true));
        spanishVoices.add(new MiniMaxVoice("Spanish_HumorousElder", "Humorous Elder", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_EnergeticBoy", "Energetic Boy", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_WhimsicalGirl", "Whimsical Girl", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_StrictBoss", "Strict Boss", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_ReliableMan", "Reliable Man", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_SereneElder", "Serene Elder", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_AngryMan", "Angry Man", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_AssertiveQueen", "Assertive Queen 👑", "Español", "Mujer", true));
        spanishVoices.add(new MiniMaxVoice("Spanish_CaringGirlfriend", "Caring Girlfriend", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_PowerfulSoldier", "Powerful Soldier ⚔️", "Español", "Hombre", true));
        spanishVoices.add(new MiniMaxVoice("Spanish_PassionateWarrior", "Passionate Warrior", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_ChattyGirl", "Chatty Girl", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_RomanticHusband", "Romantic Husband", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_CompellingGirl", "Compelling Girl", "Español", "Mujer"));
        spanishVoices.add(new MiniMaxVoice("Spanish_PowerfulVeteran", "Powerful Veteran", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_SensibleManager", "Sensible Manager", "Español", "Hombre"));
        spanishVoices.add(new MiniMaxVoice("Spanish_ThoughtfulLady", "Thoughtful Lady", "Español", "Mujer"));

        allVoices.addAll(spanishVoices);
        voicesByLanguage.put("Español", spanishVoices);

        // ============ 葡萄牙文音色 ============
        List<MiniMaxVoice> portugueseVoices = new ArrayList<>();
        portugueseVoices.add(new MiniMaxVoice("Portuguese_SentimentalLady", "Sentimental Lady", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_BossyLeader", "Bossy Leader", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Wiselady", "Wise Lady", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Strong-WilledBoy", "Strong-willed Boy", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Deep-VoicedGentleman", "Deep-voiced Gentleman", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_UpsetGirl", "Upset Girl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_PassionateWarrior", "Passionate Warrior", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_AnimeCharacter", "Anime Character 🎬", "Português", "Mulher", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_ConfidentWoman", "Confident Woman", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_AngryMan", "Angry Man", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_CaptivatingStoryteller", "Captivating Storyteller", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Godfather", "Godfather 👨‍👦‍👦", "Português", "Homem", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_ReservedYoungMan", "Reserved Young Man", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_SmartYoungGirl", "Smart Young Girl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Kind-heartedGirl", "Kind-hearted Girl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Pompouslady", "Pompous Lady", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Grinch", "Grinch 🎄", "Português", "Homem", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Debator", "Debator", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_SweetGirl", "Sweet Girl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_AttractiveGirl", "Attractive Girl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_ThoughtfulMan", "Thoughtful Man", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_PlayfulGirl", "Playful Girl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_GorgeousLady", "Gorgeous Lady", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_LovelyLady", "Lovely Lady", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_SereneWoman", "Serene Woman", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_SadTeen", "Sad Teen", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_MaturePartner", "Mature Partner", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Comedian", "Comedian", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_NaughtySchoolgirl", "Naughty Schoolgirl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Narrator", "Narrator", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_ToughBoss", "Tough Boss", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Fussyhostess", "Fussy Hostess", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Dramatist", "Dramatist", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Steadymentor", "Steady Mentor", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Jovialman", "Jovial Man", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_CharmingQueen", "Charming Queen 👑", "Português", "Mulher", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_SantaClaus", "Santa Claus 🎅", "Português", "Homem", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Rudolph", "Rudolph 🦌", "Português", "Homem", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Arnold", "Arnold 💪", "Português", "Homem", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_CharmingSanta", "Charming Santa 🎅", "Português", "Homem", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_CharmingLady", "Charming Lady", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Ghost", "Ghost 👻", "Português", "Homem", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_HumorousElder", "Humorous Elder", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_CalmLeader", "Calm Leader", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_GentleTeacher", "Gentle Teacher", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_EnergeticBoy", "Energetic Boy", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_ReliableMan", "Reliable Man", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_SereneElder", "Serene Elder", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_GrimReaper", "Grim Reaper 💀", "Português", "Homem", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_AssertiveQueen", "Assertive Queen 👑", "Português", "Mulher", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_WhimsicalGirl", "Whimsical Girl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_StressedLady", "Stressed Lady", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_FriendlyNeighbor", "Friendly Neighbor", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_CaringGirlfriend", "Caring Girlfriend", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_PowerfulSoldier", "Powerful Soldier ⚔️", "Português", "Homem", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_FascinatingBoy", "Fascinating Boy", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_RomanticHusband", "Romantic Husband", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_StrictBoss", "Strict Boss", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_InspiringLady", "Inspiring Lady", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_PlayfulSpirit", "Playful Spirit 👻", "Português", "Mulher", true));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_ElegantGirl", "Elegant Girl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_CompellingGirl", "Compelling Girl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_PowerfulVeteran", "Powerful Veteran", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_SensibleManager", "Sensible Manager", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_ThoughtfulLady", "Thoughtful Lady", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_TheatricalActor", "Theatrical Actor", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_FragileBoy", "Fragile Boy", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_ChattyGirl", "Chatty Girl", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_Conscientiousinstructor", "Conscientious Instructor", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_RationalMan", "Rational Man", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_WiseScholar", "Wise Scholar", "Português", "Homem"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_FrankLady", "Frank Lady", "Português", "Mulher"));
        portugueseVoices.add(new MiniMaxVoice("Portuguese_DeterminedManager", "Determined Manager", "Português", "Mulher"));

        allVoices.addAll(portugueseVoices);
        voicesByLanguage.put("Português", portugueseVoices);

        // ============ 法文音色 ============
        List<MiniMaxVoice> frenchVoices = new ArrayList<>();
        frenchVoices.add(new MiniMaxVoice("French_Male_Speech_New", "Level-Headed Man", "Français", "Homme"));
        frenchVoices.add(new MiniMaxVoice("French_Female_News Anchor", "Patient Female Presenter", "Français", "Femme"));
        frenchVoices.add(new MiniMaxVoice("French_CasualMan", "Casual Man", "Français", "Homme"));
        frenchVoices.add(new MiniMaxVoice("French_MovieLeadFemale", "Movie Lead Female", "Français", "Femme"));
        frenchVoices.add(new MiniMaxVoice("French_FemaleAnchor", "Female Anchor", "Français", "Femme"));
        frenchVoices.add(new MiniMaxVoice("French_MaleNarrator", "Male Narrator", "Français", "Homme"));

        allVoices.addAll(frenchVoices);
        voicesByLanguage.put("Français", frenchVoices);

        // ============ 印尼文音色 ============
        List<MiniMaxVoice> indonesianVoices = new ArrayList<>();
        indonesianVoices.add(new MiniMaxVoice("Indonesian_SweetGirl", "Sweet Girl", "Bahasa Indonesia", "Wanita"));
        indonesianVoices.add(new MiniMaxVoice("Indonesian_ReservedYoungMan", "Reserved Young Man", "Bahasa Indonesia", "Pria"));
        indonesianVoices.add(new MiniMaxVoice("Indonesian_CharmingGirl", "Charming Girl", "Bahasa Indonesia", "Wanita"));
        indonesianVoices.add(new MiniMaxVoice("Indonesian_CalmWoman", "Calm Woman", "Bahasa Indonesia", "Wanita"));
        indonesianVoices.add(new MiniMaxVoice("Indonesian_ConfidentWoman", "Confident Woman", "Bahasa Indonesia", "Wanita"));
        indonesianVoices.add(new MiniMaxVoice("Indonesian_CaringMan", "Caring Man", "Bahasa Indonesia", "Pria"));
        indonesianVoices.add(new MiniMaxVoice("Indonesian_BossyLeader", "Bossy Leader", "Bahasa Indonesia", "Pria"));
        indonesianVoices.add(new MiniMaxVoice("Indonesian_DeterminedBoy", "Determined Boy", "Bahasa Indonesia", "Pria"));
        indonesianVoices.add(new MiniMaxVoice("Indonesian_GentleGirl", "Gentle Girl", "Bahasa Indonesia", "Wanita"));

        allVoices.addAll(indonesianVoices);
        voicesByLanguage.put("Bahasa Indonesia", indonesianVoices);

        // ============ 德文音色 ============
        List<MiniMaxVoice> germanVoices = new ArrayList<>();
        germanVoices.add(new MiniMaxVoice("German_FriendlyMan", "Friendly Man", "Deutsch", "Mann"));
        germanVoices.add(new MiniMaxVoice("German_SweetLady", "Sweet Lady", "Deutsch", "Frau"));
        germanVoices.add(new MiniMaxVoice("German_PlayfulMan", "Playful Man", "Deutsch", "Mann"));

        allVoices.addAll(germanVoices);
        voicesByLanguage.put("Deutsch", germanVoices);

        // ============ 俄文音色 ============
        List<MiniMaxVoice> russianVoices = new ArrayList<>();
        russianVoices.add(new MiniMaxVoice("Russian_HandsomeChildhoodFriend", "Handsome Childhood Friend", "Русский", "Мужчина"));
        russianVoices.add(new MiniMaxVoice("Russian_BrightHeroine", "Bright Queen 👑", "Русский", "Женщина", true));
        russianVoices.add(new MiniMaxVoice("Russian_AmbitiousWoman", "Ambitious Woman", "Русский", "Женщина"));
        russianVoices.add(new MiniMaxVoice("Russian_ReliableMan", "Reliable Man", "Русский", "Мужчина"));
        russianVoices.add(new MiniMaxVoice("Russian_CrazyQueen", "Crazy Girl", "Русский", "Женщина", true));
        russianVoices.add(new MiniMaxVoice("Russian_PessimisticGirl", "Pessimistic Girl", "Русский", "Женщина"));
        russianVoices.add(new MiniMaxVoice("Russian_AttractiveGuy", "Attractive Guy", "Русский", "Мужчина"));
        russianVoices.add(new MiniMaxVoice("Russian_Bad-temperedBoy", "Bad-tempered Boy", "Русский", "Мужчина"));

        allVoices.addAll(russianVoices);
        voicesByLanguage.put("Русский", russianVoices);

        // ============ 意大利文音色 ============
        List<MiniMaxVoice> italianVoices = new ArrayList<>();
        italianVoices.add(new MiniMaxVoice("Italian_BraveHeroine", "Brave Heroine", "Italiano", "Donna"));
        italianVoices.add(new MiniMaxVoice("Italian_Narrator", "Narrator", "Italiano", "Uomo"));
        italianVoices.add(new MiniMaxVoice("Italian_WanderingSorcerer", "Wandering Sorcerer 🧙", "Italiano", "Donna", true));
        italianVoices.add(new MiniMaxVoice("Italian_DiligentLeader", "Diligent Leader", "Italiano", "Donna"));

        allVoices.addAll(italianVoices);
        voicesByLanguage.put("Italiano", italianVoices);

        // ============ 阿拉伯文音色 ============
        List<MiniMaxVoice> arabicVoices = new ArrayList<>();
        arabicVoices.add(new MiniMaxVoice("Arabic_CalmWoman", "Calm Woman", "العربية", "أنثى"));
        arabicVoices.add(new MiniMaxVoice("Arabic_FriendlyGuy", "Friendly Guy", "العربية", "ذكر"));

        allVoices.addAll(arabicVoices);
        voicesByLanguage.put("العربية", arabicVoices);

        // ============ 土耳其文音色 ============
        List<MiniMaxVoice> turkishVoices = new ArrayList<>();
        turkishVoices.add(new MiniMaxVoice("Turkish_CalmWoman", "Calm Woman", "Türkçe", "Kadın"));
        turkishVoices.add(new MiniMaxVoice("Turkish_Trustworthyman", "Trustworthy Man", "Türkçe", "Erkek"));

        allVoices.addAll(turkishVoices);
        voicesByLanguage.put("Türkçe", turkishVoices);

        // ============ 乌克兰文音色 ============
        List<MiniMaxVoice> ukrainianVoices = new ArrayList<>();
        ukrainianVoices.add(new MiniMaxVoice("Ukrainian_CalmWoman", "Calm Woman", "Українська", "Жінка"));
        ukrainianVoices.add(new MiniMaxVoice("Ukrainian_WiseScholar", "Wise Scholar", "Українська", "Чоловік"));

        allVoices.addAll(ukrainianVoices);
        voicesByLanguage.put("Українська", ukrainianVoices);
    }

    /**
     * 获取所有音色列表
     */
    public static List<MiniMaxVoice> getAllVoices() {
        return new ArrayList<>(allVoices);
    }

    /**
     * 获取所有支持的语言
     */
    public static List<String> getLanguages() {
        return new ArrayList<>(voicesByLanguage.keySet());
    }

    /**
     * 根据语言获取音色列表
     */
    public static List<MiniMaxVoice> getVoicesByLanguage(String language) {
        List<MiniMaxVoice> voices = voicesByLanguage.get(language);
        if (voices == null) {
            return new ArrayList<>();
        }
        return new ArrayList<>(voices);
    }

    /**
     * 根据voice_id查找音色
     */
    public static MiniMaxVoice findVoiceById(String voiceId) {
        for (MiniMaxVoice voice : allVoices) {
            if (voice.getVoiceId().equals(voiceId)) {
                return voice;
            }
        }
        return null;
    }

    /**
     * 获取默认音色
     */
    public static MiniMaxVoice getDefaultVoice() {
        // 默认使用青涩青年（男声）
        return findVoiceById("male-qn-qingse");
    }

    /**
     * 获取所有卡通/动漫风格音色
     */
    public static List<MiniMaxVoice> getCartoonVoices() {
        return new ArrayList<>(cartoonVoices);
    }

    /**
     * 检查是否为卡通音色
     */
    public static boolean isCartoonVoice(String voiceId) {
        MiniMaxVoice voice = findVoiceById(voiceId);
        return voice != null && voice.isCartoon();
    }

    /**
     * 获取卡通音色数量（用于调试）
     */
    public static int getCartoonVoiceCount() {
        return cartoonVoices.size();
    }
}
