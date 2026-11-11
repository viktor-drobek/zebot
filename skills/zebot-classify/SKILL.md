---
name: zebot-classify
metadata:
  version: 1.1.0
description: >
  Run when asked to label political posts (Zelensky's Telegram channel or similar speeches) with
  the ZeBot2050 propaganda-analysis classes: for every post pick exactly one class from the fixed
  vocabulary in vocab.md, or null when no class applies. Input and output are JSON Lines.
---

# ZeBot class labeling: one class or none per post

The classes come from the ZeBot2050 channel, where an analyst tags quotes of Zelensky with a tag
(мифологема, тема, цель, месседж, факт) and a short formulation, for example
`мифологема: россия — мировое зло`. This skill reproduces one reading of that scheme: **the single
class that the post as a whole is built to convey**, or `null`.

## Input and output

Input: JSON Lines, one post per line: `{"id": "21723", "text": "..."}`. Texts are usually Russian
translations; Ukrainian or English originals are labeled the same way.

Output: JSON Lines only, exactly one line per input line, in the same order, no blank lines,
nothing before or after, no code fences:

```
{"id": "21723", "class": "мифологема: россия воюет против мирного населения"}
{"id": "21671", "class": null}
```

`class` is either `null` or a string copied character for character from `vocab.md`. Never
invent, shorten or paraphrase a class. Keep it lowercase and keep «—» (em dash) and «-» exactly as
in `vocab.md`. Copy `id` exactly as given, with the same JSON type.

## Method

Work through the steps in order for every post.

1. **Service post → `null`.** «НАЖИВО», «Наживо», «В прямом эфире», «Прямая трансляция»
   началась/завершена, a video caption with no claim (e.g. «Обращение»), a bare link.
2. **Find the main point**: the point most sentences serve. A closing request overrides it only if
   it is a concrete request (weapons, air defence, money, sanctions). Ritual closings («Слава
   Україні!», «Мы победим», «Спасибо всем, кто помогает») and a general «давление на Россию» are not
   closing calls. An address with several topics: take the topic with the most sentences; on a tie,
   the first one.
3. **Map the main point to a class** with the cue table below. If a row fits, use its class even
   when `vocab.md` has a formulation that looks closer (for example
   `тема: украина скоро вступит в ес`, `мифологема: во всем путин виноват`,
   `мифологема: россия воюет против европы`,
   `тема: вооружение для украины`, `тема: украина и <country>`): the row wins. Search `vocab.md`
   only when no row fits. Never use `мифологема: россия — мировое зло` when another row fits.
4. **No fit → `null`.** If no class states the main point, answer `null`: culture awards, business
   or trade cooperation, a call or meeting with no concrete aid or request, a holiday greeting, a
   remembrance day with no claim about Russia, a patriarch's anniversary. Do not force a class onto
   a post it does not describe.
5. **Copy the exact string** from `vocab.md`, with its tag prefix.

### Cue table

| The post mainly… | Class |
|---|---|
| reports Russian strikes on people, homes, energy, railways; counts the dead and the people left without power | `мифологема: россия воюет против мирного населения` |
| is about Russia's status as a terrorist state (recognition, a tribunal, a list), not about one strike | `мифологема: россия — страна-террорист` |
| thanks one named partner (a leader, a country) for aid, a package, support | `мифологема: всесильные друзья украины` |
| stresses that many countries, a summit or «все, кто с Украиной» stand with Ukraine | `мифологема: весь мир с украиной` |
| asks for or says Ukraine needs weapons, interceptors, air defence, money, equipment | `цель: оружие и деньги для украины` |
| calls on partners for new or stronger sanctions | `цель: новые санкции` |
| reports the government's own work: a «селектор», meetings with regional heads, repairs, payments, decisions for people, investigations and dismissals, including Ukraine's own sanctions decisions | `тема: украинская власть работает на благо народа и государства` |
| reports a call or meeting with a leader and names concrete aid or a request | the row for that aid or request |
| reports military successes: liberated land, record enemy losses, a successful operation | `мифологема: украина побеждает` |
| promises or wishes victory, with no concrete success reported | `мифологема: украина победит` |
| honours the everyday courage of a named branch of the army or profession (railway, energy) | `тема: каждодневный подвиг украинцев` |
| is about EU or OECD accession, European integration | `мифологема: украина — это европа` |
| describes negotiations with Ukraine as constructive and ready, Russia expected to match | `месседж: украина хочет мира` |
| is about security guarantees for Ukraine | `тема: гарантии безопасности` |
| reports a prisoner exchange, returned children or civilians | `мифологема: украина своих не бросает` |
| says the war goes on because of Russia or Putin, «когда Путин хочет, это прекращается», including when only Putin is named | `мифологема: во всем виновата россия` |
| says Russia threatens Europe or the whole world | `мифологема: россия — угроза миру` |
| presents Ukraine's long-range strikes as a just answer to Russian aggression | `мифологема: россия — агрессор` |
| reports destroyed churches, heritage, killed clergy | `мифологема: россия — страна варваров` |
| praises the unity of the nation, the language, the people («мы вместе», no addressee) | `мифологема: украина едина и непобедима` |
| says Ukraine fights for freedom, peace and justice | `мифологема: украина сражается за мир, свободу и справедливость` |
| calls Russia evil itself, a force of evil for the whole world, with no concrete strike or event as the point | `мифологема: россия — мировое зло` |

### Ties

- When two rows fit, a concrete closing request decides; otherwise take the row most sentences
  serve; if still tied, take the row that appears first in the table.
- A post that describes strikes and then asks partners for interceptors is
  `цель: оружие и деньги для украины`; a post that only describes strikes is
  `мифологема: россия воюет против мирного населения`.
- A strike report is `мифологема: россия воюет против мирного населения` even when it calls the
  strike «террор» or the Russians «террористы».
- Thanks to one named partner is `мифологема: всесильные друзья украины`, even if the post adds
  that all partners stand with Ukraine or mentions a package, unless it ends by asking for more.
  Use `тема: украина и <country>` only for bilateral relations with no thanks for aid.
- A post that reports a concrete military success is `мифологема: украина побеждает` even if it
  ends with a promise of victory.
- Thanks to a named profession or branch is `тема: каждодневный подвиг украинцев`; praise of the
  nation as a whole is `мифологема: украина едина и непобедима`.

## Examples

These are invented for illustration and are not posts from the channel.

Input:

```
{"id": "e1", "text": "Прямая трансляция началась."}
{"id": "e2", "text": "Ночью россияне ударили по подстанциям в трёх областях. Без света остались 300 тысяч семей. Ремонтные бригады работают."}
{"id": "e3", "text": "Россия снова бьёт баллистикой по нашим городам. Нам нужны ракеты для «Патриотов». Просим партнёров не откладывать поставки."}
{"id": "e4", "text": "Благодарю Премьер-министра Норвегии за новый пакет энергетической помощи. Норвегия всегда рядом с Украиной."}
{"id": "e5", "text": "Вручил государственные награды писателям и музыкантам. Культура — это голос Украины в мире."}
```

Output:

```
{"id": "e1", "class": null}
{"id": "e2", "class": "мифологема: россия воюет против мирного населения"}
{"id": "e3", "class": "цель: оружие и деньги для украины"}
{"id": "e4", "class": "мифологема: всесильные друзья украины"}
{"id": "e5", "class": null}
```

## Vocabulary

`vocab.md` next to this file lists every allowed class, grouped by tag.
