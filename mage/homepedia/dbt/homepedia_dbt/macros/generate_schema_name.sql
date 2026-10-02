{#
  Par défaut, dbt nomme le schéma "<schéma du profil>_<+schema>" (ex. "staging_gold").
  Cette macro remplace ce comportement : +schema: gold → schéma "gold", tout simplement.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
