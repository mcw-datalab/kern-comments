create or replace function select_comments_for_object_content(opk integer, ctype text)
  returns table (
    id integer,
    depth integer) as $$
  with recursive cte (id, path, parent_id, depth)  as (
      select id,
          array[id] as path,
          parent_id,
          1 as depth
      from comments_comment
      where parent_id is null and object_pk = opk and content_type = ctype
      union all
      select comments_comment.id,
          cte.path || comments_comment.id,
          comments_comment.parent_id,
          cte.depth + 1 as depth
      from comments_comment
      join cte on comments_comment.parent_id = cte.id
      where comments_comment.object_pk = opk and comments_comment.content_type = ctype
    )
    select id, depth from cte order by path;
$$ language sql;