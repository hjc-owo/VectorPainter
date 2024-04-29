# VectorPainter

## 🔥Quickstart

### Starry

```shell
CUDA_VISIBLE_DEVICES=7 python vectorpainter.py x=stroke prompt='A horse is drinking water by the lake. van Gogh style.' target="./assets/starry.jpg" result_path='./workspace/Starry/horse_starry' seed=100
python vectorpainter.py x=stroke prompt='a photo of Sydney opera house. van Gogh style.' target="./assets/starry.jpg" result_path='./workspace/Starry/opera_starry' seed=8019
```

### Sunflowers

```shell
CUDA_VISIBLE_DEVICES=1 python vectorpainter.py x=stroke "prompt='A bouquet of roses in a vase. van Gogh style.'" target="./assets/sunflowers.jpg" x.pos_type='pos' x.pos_loss_weight=1.0 result_path='./workspace/roses_sunflowers_pos1.0' seed=100
CUDA_VISIBLE_DEVICES=1 python vectorpainter.py x=stroke "prompt='A bouquet of roses in a vase. van Gogh style.'" target="./assets/sunflowers.jpg" x.pos_type='bez' x.pos_loss_weight=1.0 result_path='./workspace/roses_sunflowers_bez1.0' seed=100
CUDA_VISIBLE_DEVICES=1 python vectorpainter.py x=stroke "prompt='A bouquet of roses in a vase. van Gogh style.'" target="./assets/sunflowers.jpg" x.pos_type='bez' x.pos_loss_weight=0.5 result_path='./workspace/roses_sunflowers_bez0.5' seed=100
```

### Field

```shell
python vectorpainter.py "prompt='A brightly colored mushroom growing on a log. van Gogh style.'" x=stroke target="./assets/Field.jpg" result_path='./workspace/Field/mushroom_Field' seed=951222
```
