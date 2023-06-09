# 本の繋がりをグラフで可視化するプロジェクト

このプロジェクトは、PythonのフレームワークであるFlaskとグラフデータベースであるNeo4jを組み合わせて、本の繋がりをグラフで可視化するためのソリューションを提供します。このプロジェクトは、本の関係性や関連性を直感的に理解しやすくするために、グラフデータベースのパワフルな機能を活用します。

## プロジェクトの目的

本は多様なテーマやジャンルで書かれており、複数の本が互いに関連しています。しかし、本の繋がりや関係性を把握することはしばしば難しい課題です。このプロジェクトは、本の関連性をグラフで視覚化することで、読者や研究者が本のネットワークをより深く理解しやすくすることを目指しています。

## 主な機能

- 本のデータのインポート: プロジェクトは、事前に収集された本のデータをNeo4jデータベースにインポートします。本の情報にはタイトル、著者、ジャンルなどが含まれます。

- グラフ可視化: Neo4jの強力なグラフデータベース機能を使用して、本の関連性をグラフとして可視化します。ノードは本を表し、エッジは本の間の関連性を示します。グラフは直感的でわかりやすく、関連する本の発見やパターンの洞察に役立ちます。

- 検索とクエリ: ユーザーは特定の本や特定のテーマに関連する本を検索するためのクエリを実行できます。クエリ結果はグラフ上でハイライトされ、関連する本のネットワークを表示します。

- インタラクティブなユーザーインターフェース: Flaskを使用して、使いやすいウェブベースのユーザーインターフェースを提供します。ユーザーはグラフをズームイン・ズームアウトしたり、ノードをクリックして詳細情報を表示したりすることができます



## アクセス方法
```python
docker-compose up
```

```python
http://127.0.0.1:5000/
http://127.0.0.1:5000/admin/

ログイン Email/Password
admin@admin.com
password

```