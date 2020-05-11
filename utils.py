numbers = ['0️⃣🔟', '1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣']
true_false = ['❌', '✅']

class ChannelNotFoundException(Exception):
    pass

def format_results(results):
    tmp = []
    for i,item in enumerate(results):
        tmp.append(f"{i+1}. {item['title']} [{item['duration']}]")

    return '\n'.join(tmp)